# -*- coding: utf-8 -*-
#
# Barebone chat engine
# @see:
#       self.valid          Second stage constructor
#       self.message()      Send a message to this engine to receive a reply
#

import os
import re
import sys
import datetime
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
try:
    # Python imports
    import nltk
    import keras
    import numpy
    import pickle
    import random
    import simplemma                                    # Good lemmatizer with local languages extensions

    # Program imports
    import log
    import users
    import intent
    import defines
    from   botserver_config import serverConfiguration
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")
    sys.exit(1)


# Parsing input arguments
class chatEngine():
    @property
    def valid(self):
        return self.__valid
    @property
    def error(self):
        return self.__error

    # Class constructor/destructor
    def __init__(self, pathProgram=None, debug=False):
        try:
            self.__pathDb     = pathProgram + os.path.sep + "db"
            self.__log        = log.writer(self.__pathDb)
            self.__debugMode  = debug
            self.reload()
            self.__valid      = True
            self.__log.Write("Engine initialized")
            config = serverConfiguration(configFile= pathProgram+os.path.sep+defines.FILE_CONFIG)
            if not config.valid: raise Exception(config.error)
            self.__threshold    = config.property['chatThreshold']
            self.__languageData = simplemma.load_data(*(config.property['language']))
            self.__ignoreWords  = ['?', '!']
        except Exception as E:
            self.__error   = str(E).strip()
            self.__valid   = False


    def reload(self):
        self.__users      = users.database(self.__pathDb)                                                   # User's list with possible knowledge about them
        self.__intents    = intent.database(self.__pathDb)                                                  # Array with all possible intents
        self.__model      = keras.models.load_model(self.__pathDb + os.path.sep + defines.FILE_MODEL)       # Applied keras model
        self.__words      = pickle.load(open(self.__pathDb + os.path.sep + defines.FILE_WORDS, 'rb'))       # Word array list
        self.__classes    = pickle.load(open(self.__pathDb + os.path.sep + defines.FILE_CLASSES, 'rb'))     # Class list, array with all "tag" items
        self.__lemmatizer = nltk.stem.WordNetLemmatizer()                                                   # Currently used lemmatizer


    def __CleanupSentence(self, message):
        # tokenize the pattern - split words into array
        sentenceWords = []
        w = nltk.word_tokenize(message)
        # stem each word - create short form for word
        sentenceWords.extend(w)
        return [simplemma.lemmatize(w.lower(), self.__languageData) for w in sentenceWords if w not in self.__ignoreWords]


    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def __bow(self, message):
        # tokenize the pattern
        sentenceWords = self.__CleanupSentence(message)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(self.__words)
        if self.__debugMode:
            print(f"        words {self.__words}\n")
        for s in sentenceWords:
            if self.__debugMode:
                print(f"        bag '{s}'")
            for i, w in enumerate(self.__words):
                if w == s:
                    # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    if self.__debugMode:
                        print(f"            MATCH  ->  {{pos:{i+1}, word:{w}}}")
        return(numpy.array(bag))

    # Predict possible match with user's message
    def __predictClass(self, message=None):
        # filter out predictions below a threshold
        p = self.__bow(message)
        res = self.__model.predict(numpy.array([p]))[0]
        results = [[i,r] for i,r in enumerate(res) if r>self.__threshold]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.__classes[r[0]], "probability": str(r[1])})
        if self.__debugMode:
            print(f"        predict\n            {return_list}")                 # [{'intent': '...', 'probability': '...'}]
        return return_list

    def __setContext(self, message=None, username=None, intents=[]):
        if not message or not username or intents==[]:
            return


    def __getResponse(self, intents):
        tag = intents[0]['intent']
        for i in self.__intents.list['intents']:
            if (i['tag']== tag):
                result = random.choice(i['responses'])
                break
        if self.__debugMode:
            print(f'        random\n            "{result}"')
        return result

    def __evaluate(self, accumulator, remainder, username):
        matches = re.finditer(defines.REGEX, remainder, re.MULTILINE)
        try:
            item = next(matches)
            value = self.__evaluateValue(originalValue=item.group(), username=username)
            (accumulator, remainder) = self.__evaluate(accumulator + remainder[:item.start()] + value, remainder[item.end():], username)
        except StopIteration as it:
            accumulator += remainder
        return (accumulator, remainder)

    # Evaluating variables substitutions and sandboxed functions only, it won't be a plain eval() on everything
    def __evaluateValue(self, originalValue=None, username=None):
        evaluate = originalValue[2:-2].split(',')           # Remove {{}} and arg split
        if len(evaluate) == 0:
            return ''

        elif evaluate[0] == 'user':                         # User defined information, '' on None
            if len(evaluate) < 2:
                return ''
            value = self.__users.data(Username=username, Variable=evaluate[1])
            if evaluate[1]=='name' and value is None:               # Name not found, picking username instead
                value = self.__users.data(Username=username, Variable='username')
            return '' if not value else value

        elif evaluate[0] == 'datetime':                     # datetime functions  (evaluate[1]: datetime format)
            if len(evaluate) < 2:
                evaluate.append('%H:%M')
            now = datetime.datetime.now()
            return now.strftime(evaluate[1])
        return "(unknown command)"                          # ?


    # Send a <message> to <username>
    # @param  username (String) Referred user
    # @param  message  (String) Dedicated message
    #
    # @return (None)   If message is invalid
    # @return (String) Replied message
    def message(self, username=None, message=None):
        if not username or not message:
            return None
        if self.__debugMode:
            print("^" * 60)
        intents = self.__predictClass(message=message)                          # Get prediction class
        self.__setContext(message=message, username=username, intents=intents)  # Context setup (if any) for predicted reply
        result = self.__getResponse(intents)                                    # Get possible response and reply it back [result]
        (result, _) = self.__evaluate("", result, username)                     # Post processing evaluation
        if self.__debugMode:
            print("_" * 60)
        self.__log.Write(msgtype='message', message1=message, message2=result)
        return result
