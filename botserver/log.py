# -*- coding: utf-8 -*-
#
# chat engine log class
#

# Program imports
try:
    import os
    import sys
    import csv
    import datetime
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")
    sys.exit(1)

# chat engine log writer [import log=log.writer()]
class writer():
    # Class constructor/destructor
    def __init__(self, path=None):
        self.__logFile = None
        filename = path + os.path.sep + 'chat.log'
        self.__csvfile = open(filename, 'a+')
        self.__logFile = csv.writer(self.__csvfile, delimiter='|')
        if self.__logFile == None:
            raise ValueError(f"Cannot open '{filename}' for writing")
    
    def Write(self, msgtype='system', message1='', message2=None, message3=None, message4=None):
        logline = [datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d %H:%M:%S'), msgtype, message1]
        if message2:
            logline += [message2]
        if message3:
            logline += [message3]
        if message4:
            logline += [message4]
        self.__logFile.writerow(logline)
        self.__csvfile.flush()
