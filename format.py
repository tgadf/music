# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 19:28:25 2017

@author: tgadfort
"""


def makeCamelCase(val):
    vals = val.split()
    if len(vals) > 1:
        nval = [x.title() if len(x) > 2 else x for x in vals]
        return " ".join(nval)
    return val
    
    