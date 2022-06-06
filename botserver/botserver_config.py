#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Python botserver daemon
#

# Program imports
import os
import sys
import argparse
try:
    import yaml
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")
    sys.exit(1)

# Parsing input arguments
class serverConfiguration():
    def __init__(self, configFile=None):
        self._errorMessage = ''
        if not configFile:
            parser = argparse.ArgumentParser(prog='botserver', description='Botserver internal daemon')
            parser.add_argument('-c', '--configuration', metavar='CONFIG', type=str, help='Server configuration file [default: config.yaml]', default='config.yaml')
            args = parser.parse_args()
            self.__filename = args.configuration
        else:
            self.__filename = configFile
        self.__path = self.__pathDB = self._property = None
        self.__valid = False
        try:
            # yaml loading
            config = yaml.load(self.filename, Loader=yaml.SafeLoader)
            with open(self.filename, 'r') as fHandler:
                config = yaml.safe_load(fHandler)
            if 'botserverHost'    not in config: raise Exception("[botserverHost] not found in configuration file")
            if 'botserverPort'    not in config: raise Exception("[botserverPort] not found in configuration file")
            if 'allowedClients'   not in config: raise Exception("[allowedClients] not found in configuration file")
            if 'botserverTimeout' not in config: config['botserverTimeout'] = 30
            if 'language'         not in config: config['language'] = ['en']        # Default language if not defined
            self._property = config
            # Checking existence of Server and CA certs
            dirCertificates = os.path.dirname(self.filename)
            dirCertificates = ('.' if dirCertificates=='' else dirCertificates) + os.path.sep + 'certs' + os.path.sep
            self.caCertificate      = self.__checkFile(dirCertificates, "ca_cert.pem")
            self.serverCertificate  = self.__checkFile(dirCertificates, "server_cert.pem")
            self.serverKey          = self.__checkFile(dirCertificates, "server_key.pem")

            self.__initFileSystem()                         # Program path and dir init

        except Exception as E:
            self._errorMessage = str(E)
            return
        # object loaded successfully
        self.__valid = True

    def __initFileSystem(self):
        try:
            self.__pathDB = os.path.dirname(self.filename)
            self.__pathDB = ('.' if self.__pathDB=='' else self.__pathDB) + os.path.sep + 'db'
            if not os.path.exists(self.pathDatabase):
                os.mkdir(self.pathDatabase)
            if not os.path.isdir(self.pathDatabase):
                raise ValueError(f'{self.pathDatabase} is not a directory')
        except Exception as E:
            raise ValueError(str(E))

    def __checkFile(self, dir, filename):
        if os.path.exists(dir + filename):
            return dir+filename
        else:
            raise Exception(f"File  {dir}{filename}  not found")

    @property
    def path(self):
        return self.__path
    @property
    def pathDatabase(self):
        return self.__pathDB
    @property
    def filename(self):
        return self.__filename
    @property
    def valid(self):
        return self.__valid
    @property
    def errorMessage(self):
        return self._errorMessage
    @property
    def property(self):
        return self._property
