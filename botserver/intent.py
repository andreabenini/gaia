# -*- coding: utf-8 -*-
#
# Load available intents (*.json) from [./db] directory
#

# Program imports
try:
    import os
    import json
    import glob
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")

# intents knowledge database [import log=log.writer()]
class database():
    @property
    def list(self):
        return self.__intents

    # Constructor
    def __init__(self, path):
        self.__intents = {}
        self.__intents['intents'] = []
        intentList = glob.glob(path + os.path.sep + '*.json')
        for filename in intentList:
            with open(filename , 'r') as jsonFile:
                self.__intents['intents'] += json.load(jsonFile)
