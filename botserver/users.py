# -*- coding: utf-8 -*-
#
# User database class, dealing with user personal data
#

try:
    # Python imports
    import yaml
    import atexit
    # Program imports
    import os
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")

# Parsing input arguments
class database():
    # Class constructor/destructor
    def __init__(self, path=None):
        self.__filename = path + os.path.sep + 'users.yaml'
        if not os.path.exists(self.__filename):
            open(self.__filename, 'a').close()
        if not os.path.isfile(self.__filename):
            raise ValueError(f"Cannot access '{self.__filename}'")
        with open(self.__filename, 'r') as fHandler:
            self.__db = yaml.safe_load(fHandler)
            fHandler.close()
        if not self.__db or self.__db==[] or self.__db=='':
            self.__db = {}
        atexit.register(self.destructor)

    def destructor(self):           # Don't use __del__(), use this hack instead
        with open(self.__filename, 'w') as fHandler:
            yaml.dump(self.__db, fHandler)


    # Return user info from database
    def user(self, Username=None):
        if not Username:
            return None
        if not Username in self.__db:
            self.__db[Username] = {}
        return self.__db[Username]
