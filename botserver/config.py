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
    def __init__(self):
        parser = argparse.ArgumentParser(prog='botserver', description='Botserver internal daemon')
        parser.add_argument('-c', '--configuration', metavar='CONFIG', type=str, help='Server configuration file [default: config.yaml]', default='config.yaml')
        args = parser.parse_args()
        self._errorMessage = ''
        self._filename = args.configuration
        self._path = self._pathDB = self._property = None
        self._valid = False
        try:
            # yaml loading
            with open(self.filename, 'r') as fHandler:
                config = yaml.safe_load(fHandler)
            if 'botserverHost'    not in config: raise Exception("[botserverHost] not found in configuration file")
            if 'botserverPort'    not in config: raise Exception("[botserverPort] not found in configuration file")
            if 'allowedClients'   not in config: raise Exception("[allowedClients] not found in configuration file")
            if 'botserverTimeout' not in config: config['botserverTimeout'] = 30
            self._property = config
            # Checking existence of Server and CA certs
            dirCertificates = os.path.dirname(self.filename)
            dirCertificates = ('.' if dirCertificates=='' else dirCertificates) + os.path.sep + 'certs' + os.path.sep
            self.caCertificate      = self.__checkFile(dirCertificates, "ca_cert.pem")
            # self.caKey              = self.__checkFile(dirCertificates, "ca_key.pem") TODO: is this needed ?
            self.serverCertificate  = self.__checkFile(dirCertificates, "server_cert.pem")
            self.serverKey          = self.__checkFile(dirCertificates, "server_key.pem")

            self.__initFileSystem()                         # Program path and dir init

        except Exception as E:
            self._errorMessage = str(E)
            return
        # object loaded successfully
        self._valid = True

    def __initFileSystem(self):
        try:
            self._pathDB = os.path.dirname(self.filename)
            self._pathDB = ('.' if self._pathDB=='' else self._pathDB) + os.path.sep + 'db'
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
        return self._path
    @property
    def pathDatabase(self):
        return self._pathDB
    @property
    def filename(self):
        return self._filename
    @property
    def valid(self):
        return self._valid
    @property
    def errorMessage(self):
        return self._errorMessage
    @property
    def property(self):
        return self._property
