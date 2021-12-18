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
        self._property = None
        self._valid = False
        try:
            # yaml loading
            with open(self.filename, 'r') as fHandler:
                config = yaml.safe_load(fHandler)
            if 'botserverHost' not in config: raise Exception("[botserverHost] not found in configuration file")
            if 'botserverPort' not in config: raise Exception("[botserverPort] not found in configuration file")
            self._property = config

            # Checking existence of Server and CA certs
            dirCertificates = os.path.dirname(self.filename)
            dirCertificates = ('.' if dirCertificates=='' else dirCertificates) + os.path.sep + 'certs' + os.path.sep
            if os.path.exists(dirCertificates + "CA.crt"):
                self.caCertificate = dirCertificates + 'CA.crt'
            else:
                raise Exception(f"File  {dirCertificates}CA.crt  not found")
            if os.path.exists(dirCertificates + "CA.pem"):
                self.caKey = dirCertificates + 'CA.pem'
            else:
                raise Exception(f"File  {dirCertificates}CA.pem  not found")
            if os.path.exists(dirCertificates + "server.pem"):
                self.serverKey = dirCertificates + 'server.pem'
            else:
                raise Exception(f"File  {dirCertificates}server.pem  not found")

        except Exception as E:
            self._errorMessage = str(E)
            return
        # object loaded successfully
        self._valid = True


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
