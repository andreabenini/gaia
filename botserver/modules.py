# -*- coding: utf-8 -*-
#
# chat engine modules class
#

# Program imports
try:
    import os
    import sys
    import importlib
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")
    sys.exit(1)

# chat engine log writer [import log=log.writer()]
class modules():
    # Class constructor/destructor
    def __init__(self, path=None, configuration=None):
        self.__path = path
        self.__config = configuration
    
    # Load/Reload active modules
    def load(self):
        for file in os.listdir(self.__path):
            if file.endswith('.py'):
                name = 'module.'+file[:-3]
                globals()[name] = importlib.import_module(name)
                globals()[name] = importlib.reload(globals()[name])

    # Detect if a module is available or not
    # @return (bool) True/False if module is loaded
    def available(self, moduleName):
        return f'module.{moduleName}' in globals()

    # Execute specified module with additional parameters, if any
    def execute(self, moduleName, parameters):
        config = self.__config[moduleName] if moduleName in self.__config else None
        return globals()['module.'+moduleName].reply(parameters, config)
