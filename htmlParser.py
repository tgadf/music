#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 08:50:54 2017

@author: tgadfort
"""

from bs4 import BeautifulSoup, element

def getHTML(htmldata, allowError = False, debug = False):
    if not isinstance(htmldata, file):
        try:
            htmldata = open(htmldata)
        except:
            raise ValueError("Could not read from",htmldata)

    try:
        bsdata = BeautifulSoup(htmldata)
    except:
        if allowError:
            return None
        else:
            raise ValueError("Could not parse html data!")

    return bsdata


def isBS4(bsdata, debug = False):
    if bsdata:
        return isinstance(bsdata, BeautifulSoup)
    return False


def isBS4Tag(bsdata, debug = False):
    if bsdata:
        return isinstance(bsdata, element.Tag)
    return False


### BeautifulSoup functions
def removeTag(line, tag, debug = False):
    if not isBS4(line) and not isBS4Tag(line):
        try:
            line = BeautifulSoup(line)
        except:
            raise ValueError("Could not create BS data from",line)
    
    if debug:
        print "Removing <"+tag+"from line: "+line
    
    tagVals = line.findAll(tag)
    for tagVal in tagVals:
        tagVal.extract()
        
    return line