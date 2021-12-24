#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Barebone chat engine
# @see:
#       self.valid          Second stage constructor
#       self.message()      Send a message to this engine to receive a reply
#

# Program imports
try:
    import os
    import csv
    import datetime
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")

# Parsing input arguments
class chatEngine():
    @property
    def valid(self):
        return self._valid
    @property
    def error(self):
        return self._error

    # Class constructor
    def __init__(self, pathDatabase=None):
        try:
            self._path  = pathDatabase
            self._logInit()
            self._logWrite("Engine initialized")
            self._valid = True
        except Exception as E:
            self._error = str(E).strip()
            self._valid = False

    # Logging methods
    def _logInit(self):
        filename = self._path + os.path.sep + 'chat.log'
        self._logFile = None
        csvfile = open(filename, 'a+')
        self._logFile = csv.writer(csvfile, delimiter='|')
        if self._logFile == None:
            raise ValueError(f"Cannot open '{filename}' for writing")
    def _logWrite(self, message1='', message2=None, msgtype='SYSTEM'):
        logline = [datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d %H:%M:%S'), msgtype, message1]
        if message2:
            logline += [message2]
        self._logFile.writerow(logline)


    # Send a <message> to <username>
    # @param  username (String) Referred user
    # @param  message  (String) Dedicated message
    #
    # @return (None)   If message is invalid
    # @return (String) Replied message
    def message(self, username=None, message=None):
        if not username or not message:
            self._valid = False
            return None
        # just a stub. Dummy output until I get something useful
        return f"{username}: {message}"
