# -*- coding: utf-8 -*-
#
# Barebone chat engine
# @see:
#       self.valid          Second stage constructor
#       self.message()      Send a message to this engine to receive a reply
#

try:
    # Python imports
    # Program imports
    import log
    import users
    import intent
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")

# Parsing input arguments
class chatEngine():
    @property
    def valid(self):
        return self.__valid
    @property
    def error(self):
        return self.__error

    # Class constructor/destructor
    def __init__(self, pathDatabase=None):
        try:
            self.__path    = pathDatabase
            self.__log     = log.writer(self.__path)
            self.__users   = users.database(self.__path)
            self.__intents = intent.database(self.__path)
            self.__valid   = True
            self.__log.Write("Engine initialized")
        except Exception as E:
            self.__error   = str(E).strip()
            self.__valid   = False
    def __del__(self):
        print("Exterminate !")


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
        # just a stub. Dummy output until I get something useful
        result = f"{username}: {message}"
        self.__log.Write(msgtype='message', message1=message, message2=result)
        return result
