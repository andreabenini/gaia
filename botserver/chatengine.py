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
    import string
    import simplemma                                    # Good lemmatizer with local languages extensions

    # Program imports
    import log
    import users
    import intent
    import defines
    import modules
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
            config = serverConfiguration(configFile= pathProgram+os.path.sep+defines.FILE_CONFIG)
            if not config.valid: raise Exception(config.error)
            self.__threshold    = config.property['chatThreshold']
            self.__languageData = simplemma.load_data(*(config.property['language']))
            #
            self.__pathDb       = pathProgram + os.path.sep + "db"
            self.__modules      = modules.modules(pathProgram+os.path.sep+"botserver"+os.path.sep+"module", config.property['plugin'])
            self.__log          = log.writer(self.__pathDb)
            self.__sys          = {}            # Internal engine dict, used in self.__evaluate()
            self.__debugMode    = debug
            self.reload()
            self.__valid        = True
            self.__log.Write(message1='INFO', message2="Engine initialized")
        except Exception as E:
            self.__error   = str(E).strip()
            self.__valid   = False

    def __debug(self, message):
        if self.__debugMode:
            print(message)

    def reload(self):
        self.__users   = users.database(self.__pathDb)                                                   # User's list with possible knowledge about them
        self.__intents = intent.database(self.__pathDb)                                                  # Array with all possible intents
        self.__model   = keras.models.load_model(self.__pathDb + os.path.sep + defines.FILE_MODEL)       # Applied keras model
        self.__words   = pickle.load(open(self.__pathDb + os.path.sep + defines.FILE_WORDS, 'rb'))       # Word array list
        self.__classes = pickle.load(open(self.__pathDb + os.path.sep + defines.FILE_CLASSES, 'rb'))     # Class list, array with all "tag" items
        self.__modules.load()


    def __CleanupSentence(self, message):
        # tokenize the pattern - split words into array
        sentenceWords = []
        w = nltk.word_tokenize(message)
        # stem each word - create short form for word
        sentenceWords.extend(w)
        return [simplemma.lemmatize(w.lower(), self.__languageData) for w in sentenceWords if w not in defines.IGNORE_WORDS]


    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def __bow(self, message):
        # tokenize the pattern
        sentenceWords = self.__CleanupSentence(message)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(self.__words)
        matchList = []
        self.__debug(f"        words {self.__words}\n")
        for s in sentenceWords:
            matchList.append(s)
            self.__debug(f"        bag '{s}'")
            for i, w in enumerate(self.__words):
                if w == s:
                    # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    self.__debug(f"            MATCH  ->  {{pos:{i+1}, word:{w}}}")
        return (numpy.array(bag), matchList)

    # Predict possible matches from user's message
    # @return (list) array of dicts {"intent": intentName, "probability": percentage}
    def __predictClass(self, message=None):
        # filter out predictions below a threshold
        (p, matchPhrase) = self.__bow(message)
        res = self.__model.predict(numpy.array([p]))[0]
        results = [[i,r] for i,r in enumerate(res) if r>self.__threshold]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.__classes[r[0]], "probability": str(r[1])})
        self.__debug(f"        predict\n            {return_list}")                 # [{'intent': '...', 'probability': '...'}]
        return (return_list, matchPhrase)

    # @param message  (string)          User's message
    # @param username (string)          current username
    # @param intents  (list of dicts)   array of intents: [{'intent': 'intentName', 'probability': '0.9994666'}]
    # @param variables (dict)           dictionary of new vars for [username]
    def __setContext(self, message=None, username=None, intents=[], variables={}):
        if not message or not username or intents==[]:
            return
        # Set [variables] list detected from user's message
        for variable in variables:
            self.__debug("        set "+("["+username+"]").ljust(20) + f"{variable} = {variables[variable]}")
            self.__users.set(Username=username, Variable=variable, Value=variables[variable])


    # Detect closest users' phrase and assign possible variables in between
    # @param intents (list)   List of possible intent responses, example: [{"intent": intentName, "probability": percentage}]
    # @param phrase  (string) User's phrase
    # @return (dict) dictionary with user's variables
    def __detectUserVariables(self, intents=[], phrase=None):
        if len(intents) <= 0 or not phrase:
            return {}
        replyIntentList = self.__detectUserVariablesIntent(intents[0]['intent'])    # Get first intent only
        matchWords = 0
        matchStatement = []
        varList = {}
        index = 0
        matchIndex = -1
        for intent in replyIntentList:
            (varMasked, _, varList) = self.__detectUserVariablesSubstitute('', intent, varList)
            intent = self.__CleanupSentence(varMasked)
            intent = self.__detectUserVariablesReassign(intent, varList)
            (matchWords, matchStatement, matchIndex) = self.__detectUserVariablesBestMatch(intent, phrase, index, matchWords, matchStatement, matchIndex)
            index += 1
        self.__debug(f'        matching ({matchWords} times) -> {matchStatement}\n            index({matchIndex}) -> {phrase}')
        return self.__detectUserVariablesAssign(matchStatement, phrase)             # Assign vars detected from user's phrase, if any

    # @return (list) intent matching array statements
    def __detectUserVariablesIntent(self, intentName):
        for item in self.__intents.list['intents']:
            if item['tag'] == intentName:
                return item['patterns']
        return []
    # Substitute variable pattern '{{whatever}}' with random string in order to avoid messes with the lemmatizer
    # @return (accumulator, leftPart, variableList)
    #           accumulator  (string) Result string with all '{{var}}' substituted with random strings
    #           leftPart     (_)      insignificant, string left to process (recursively). Should be '' at the end
    #           variableList (dict)   Dictionary with the var list, something like: {'{{name,*}}': 'QYTXDKBIGFAOJYMFRIKJ', '{{name}}': 'PINSQGTNVRHUVXRRTXIX'}
    def __detectUserVariablesSubstitute(self, accumulator, phrase, varList):
        try:
            matches = re.finditer(defines.REGEX, phrase, re.MULTILINE)
            item = next(matches)
            key = item.group()
            if key not in varList:
                varList[key] = ''.join(random.choice(string.ascii_lowercase) for x in range(20))
            (accumulator, phrase, varList) = self.__detectUserVariablesSubstitute(accumulator+phrase[:item.start()]+varList[key], phrase[item.end():], varList)
        except StopIteration as it:
            accumulator += phrase
        return (accumulator, phrase, varList)
    # @param intent  (list) System intent matched with random string instead of vars
    # @param varList (dict) Dictionary with the variables list
    def __detectUserVariablesReassign(self, intent, varList):
        for item in range(len(intent)):
            for variable in varList:
                if varList[variable] == intent[item]:
                    intent[item] = variable
        return intent
    # Detect how [intent] is close to users' [phrase]
    # @param intent         (array)  System intent to evaluate
    # @param phrase         (string) Current user phrase
    # @param matchWords     (int)    Current best match word count on system intents
    # @param matchStatement (array)  Current best match sentence on system intents
    def __detectUserVariablesBestMatch(self, intent, phrase, index, matchWords, matchStatement, matchIndex):
        count = 0
        for word in phrase:
            if word in intent:
                count += 1
        if count > matchWords:
            return (count, intent, index)
        return (matchWords, matchStatement, matchIndex)
    # Assign variables from user's [userPhrase], accordingly to [systemIntent] matched statement
    # @param  systemIntent (list) Detected system intent, list of words
    # @param  userPhrase   (list) User's phrase, list of words
    # @return (dict) Variables detected from user's phrase and assignable as user's context
    # @see next call: self.__setContext()
    def __detectUserVariablesAssign(self, systemIntent, userPhrase):
        variableDict = {}
        for word in systemIntent:
            if word in userPhrase:                                  # Delete similar words from [userPhrase]
                pos = userPhrase.index(word)
                userPhrase = userPhrase[pos+1:]
            else:
                if word[0:2]=='{{' and word[-2:]=='}}':             # Strip '{{','}}'
                    evalString = word[2:-2].split(',')
                    varName  = evalString[0] if len(evalString)>=1 else None
                    varValue = evalString[1] if len(evalString)>=2 else None
                    if varName and not varValue:                    # word = '{{name}}'
                        variableDict[varName] = userPhrase[0]        if len(userPhrase)>0 else None
                        userPhrase            = userPhrase[1:]       if len(userPhrase)>1 else []
                    if varName and varValue:                        # word = '{{name,*}}'
                        variableDict[varName] = ' '.join(userPhrase) if len(userPhrase)>0 else None
                        userPhrase            = []
        return variableDict


    # Reply back to user, pick a random response from available response list
    def __getResponse(self, intents):
        if len(intents) == 0 or not intents:
            intents = [{'intent': 'noanswer', 'probability': '1.00'}]       # Don't know what it is, taking evasive action
        tag = intents[0]['intent']
        for i in self.__intents.list['intents']:
            if i['tag']== tag:
                result = random.choice(i['responses'])
                break
        self.__debug(f'        random reply\n            "{result}"')
        return result


    # Post processing evaluation, after picking a random reply it substitues user's environment vars
    # @param accumulator (string) '' empty string at the beginning (recursive function), will contain the reply at the end
    # @param remainder   (string) part of the string I still need to evaluate (selected user reply at the beginning)
    # @param username    (string) Current username
    # @return (tuple:[string,string])=(reply,'') System reply with all substitutions already in place
    #
    # @see Called from message() reply
    def __evaluate(self, accumulator, remainder, username):
        matches = re.finditer(defines.REGEX, remainder, re.MULTILINE)
        try:
            item = next(matches)
            value = self.__evaluateValue(originalValue=item.group(), username=username)
            self.__debug(f'                - {item.group()} = {value}')
            (accumulator, remainder) = self.__evaluate(accumulator + remainder[:item.start()] + value, remainder[item.end():], username)

        # Dynamic modules error handling
        except ValueError as valError:
            remainder   = ''
            accumulator = 'ERROR'
            self.__sys['module']  = valError.args[0]
            moduleError = valError.args[1]
            self.__debug(f'        ERROR, module [{self.__sys["module"]}]\n            '+moduleError)
            self.__log.Write(message1='ERROR', message2=moduleError)
            for intent in self.__intents.list['intents']:
                if intent['tag'] == 'moduleerror':
                    result = random.choice(intent['responses'])
                    (accumulator, _) = self.__evaluate('', result, username)

        # Loop stop, normal exit. Resuming operations
        except StopIteration:
            accumulator += remainder
        return (accumulator, remainder)


    # Evaluating variables substitutions and sandboxed functions only
    # It won't NEVER be a plain eval() on everything (eval are pure evil)
    def __evaluateValue(self, originalValue=None, username=None):
        evaluate = originalValue[2:-2].split(',')                       # Remove {{}} and arg split
        if len(evaluate) == 0:
            return ''

        # User defined information, '' on None
        elif evaluate[0] == 'user':
            if len(evaluate) < 2:
                return ''
            value = self.__users.data(Username=username, Variable=evaluate[1])
            if evaluate[1]=='name' and value is None:                   # Name not found, picking username instead
                value = self.__users.data(Username=username, Variable='username')
            return '' if not value else value

        # Internal module dictionary set, see (self.__evaluate([ValueError])) exception handling
        elif evaluate[0] == 'module':       
            return self.__sys['module']

        # Dynamically execute a bot module from (module.*)
        elif self.__modules.available(evaluate[0]):
            return self.__modules.execute(evaluate[0], evaluate[1:])    # Slicing from 2nd element

        # ?
        return "(unknown command)"


    # Send a <message> to <username>
    # @param  username (String) Referred user
    # @param  message  (String) Dedicated message
    #
    # @return (None)   If message is invalid
    # @return (String) Replied message
    def message(self, username=None, message=None):
        if not username or not message:
            return None
        self.__debug("DEBUG MODE "+"^" * 59)
        (intents, phrase) = self.__predictClass(message=message)                # Get prediction class
        variables = self.__detectUserVariables(intents=intents, phrase=phrase)  # Detect user variables from phrase
        self.__setContext(message=message, username=username, intents=intents, variables=variables)     # Context setup (if any) for predicted reply
        result = self.__getResponse(intents)                                    # Get possible response and reply it back [result]
        (result, _) = self.__evaluate("", result, username)                     # Post processing evaluation (variables substitution from environment data)
        self.__debug("_"*70 + "\n")
        if len(intents) == 0:
            self.logQuery(username, message)
        self.__log.Write(msgtype='message', message1=username, message2=message, message3=result)
        return result


    # Mark query into logfile as 'question not found' so it can be evaluated later on
    def logQuery(self, username, message, msgtype='ERROR', reason='QUESTION NOT FOUND'):
        self.__log.Write(message1=msgtype, message2=reason, message3=username, message4=message)
