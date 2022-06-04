# -*- coding: utf-8 -*-
#
# Barebone chat engine
# @see:
#       self.valid          Second stage constructor
#       self.message()      Send a message to this engine to receive a reply
#

import os
import sys
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

    # Program imports
    import log
    import users
    import intent
    import defines
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
    def __init__(self, pathDatabase=None, debug=False):
        try:
            self.__path       = pathDatabase
            self.__log        = log.writer(self.__path)
            self.__debugMode  = debug
            self.reload()
            self.__valid      = True
            self.__log.Write("Engine initialized")
        except Exception as E:
            self.__error   = str(E).strip()
            self.__valid   = False


    def reload(self):
        self.__users      = users.database(self.__path)
        self.__intents    = intent.database(self.__path)
        self.__model      = keras.models.load_model(self.__path + os.path.sep + defines.FILE_MODEL)
        self.__words      = pickle.load(open(self.__path + os.path.sep + defines.FILE_WORDS, 'rb'))
        self.__classes    = pickle.load(open(self.__path + os.path.sep + defines.FILE_CLASSES, 'rb'))
        self.__lemmatizer = nltk.stem.WordNetLemmatizer()


    def __CleanupSentence(self, message):
        # tokenize the pattern - split words into array
        sentenceWords = nltk.word_tokenize(message)
        # stem each word - create short form for word
        sentenceWords = [self.__lemmatizer.lemmatize(word.lower()) for word in sentenceWords]
        return sentenceWords

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def __bow(self, message):
        # tokenize the pattern
        sentenceWords = self.__CleanupSentence(message)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(self.__words)
        for s in sentenceWords:
            if self.__debugMode:
                print(f"        bag [{s}]")
            for i, w in enumerate(self.__words):
                if w == s:
                    # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    if self.__debugMode:
                        print(f"         ->  {w}")
        return(numpy.array(bag))


    def __predictClass(self, message=None):
        # filter out predictions below a threshold
        p = self.__bow(message)
        res = self.__model.predict(numpy.array([p]))[0]
        ERROR_THRESHOLD = 0.25      # FIXME: Set it as a parameter
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.__classes[r[0]], "probability": str(r[1])})
        return return_list

    def __getResponse(self, intents):
        tag = intents[0]['intent']
        for i in self.__intents.list['intents']:
            if (i['tag']== tag):
                result = random.choice(i['responses'])
                break
        return result


    # Send a <message> to <username>
    # @param  username (String) Referred user
    # @param  message  (String) Dedicated message
    #
    # @return (None)   If message is invalid
    # @return (String) Replied message
    def message(self, username=None, message=None):
        if not username or not message:
            self.__valid = False
            return None
        _ = self.__users.user(Username=username)
        # Get prediction class
        intents = self.__predictClass(message=message)
        print(f"        {intents}")
        # Get response and reply it back
        result = self.__getResponse(intents)
        self.__log.Write(msgtype='message', message1=message, message2=result)
        return result
