#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Python botserver daemon
#

# Program imports
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
        self._filename = args.configuration
        # yaml loading
        self._property = None
        self._valid = False
        try:
            with open(self.filename, 'r') as fHandler:
                config = yaml.safe_load(fHandler)
            if 'secret'         not in config: return
            if 'botserverHost'  not in config: return
            if 'botserverPort'  not in config: return
            self._property = config
            self._valid = True
        except Exception as E:
            pass

    @property
    def filename(self):
        return self._filename
    @property
    def valid(self):
        return self._valid
    @property
    def property(self):
        return self._property

