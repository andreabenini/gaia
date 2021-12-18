#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Python botserver daemon
#

# Program imports
try:
    import yaml
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")

# Parsing input arguments
class chatEngine():
    @property
    def valid(self):
        return self._valid

    def __init__(self):
        self._valid = True

    def message(self, username=None, message=None):
        if not username or not message:
            return None
        return f"{username}: {message}"
