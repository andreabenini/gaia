# -*- coding: utf-8 -*-
#
# weather dynamic module
#
# @return reply(inputList, configuration) -> string with required output
#
#
import json
import requests

def reply(inputList=None, config=None):
    if len(inputList) == 0:
        inputList.append('temperature')     # Default command
    # Get current temperature
    if inputList[0] == 'temperature':
        return temperature(inputList[1:], config)
    # unknown command
    else:
        return '?'

def temperature(parameters, config):
    try:
        # Input parameters
        if len(parameters) == 0:
            parameters.append('now')
        if len(parameters) < 2:
            parameters.append(config['units'])
        # Get temp information from remote
        unit = parameters[1].lower() if parameters[1].lower() in ['metric', 'imperial'] else config['units'].lower()
        url  = f'https://api.openweathermap.org/data/2.5/weather?lat={config["lat"]}&lon={config["lon"]}&appid={config["api"]}&units={unit}'
        response = requests.get(url)
        data = json.loads(response.text)
        result = str(data['main']['temp'])+'°' + ('F' if unit=='imperial' else 'C')
        return result
    except Exception as E:
        # Format: (ModuleName, ErrorString)
        raise ValueError('weather', 'module [weather] '+str(E))
