# -*- coding: utf-8 -*-
#
# datetime dynamic module
#
# @return reply(inputList, configuration) -> string with required output
#
#
import datetime

def reply(inputList=None, _config=None):
    if len(inputList) == 0:
        inputList.append('%H:%M')
    now = datetime.datetime.now()
    return now.strftime(inputList[0])
