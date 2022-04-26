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
        csvfile = open(filename, 'a+')
        self.__logFile = csv.writer(csvfile, delimiter='|')
        if self.__logFile == None:
            raise ValueError(f"Cannot open '{filename}' for writing")
    
    def Write(self, message1='', message2=None, msgtype='system'):
        logline = [datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d %H:%M:%S'), msgtype, message1]
        if message2:
            logline += [message2]
        self.__logFile.writerow(logline)
