# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 20:06:26 2017

@author: tgadfort
"""

from unicodedata import normalize

def isUnicode(name):
    if name:
        return isinstance(name,unicode)
    return False



def makeUnicode(name, debug = False):    
    if isUnicode(name):
        return name
    
    try:
        if isinstance(name, int) or isinstance(name, float):
            name = str(name)
        retval = unicode(name, 'utf-8')
    except:
        if debug:
            print "Could not create unicode for:",name
        retval = None
        
    return retval



def normalizeUnicode(name, ext="NFD"):
    uname   = makeUnicode(name)
    if isUnicode(uname):
        normval = normalize(ext, uname)
    else:
        normval = None
    return normval



def makeStrFromUnicode(name):
    normval = normalizeUnicode(name)
    if isUnicode(normval):
        strval  = normval.encode('utf-8')
    else:
        strval  = None
    return strval



def makeNumeric(value, debug = False):    
    if isinstance(value, int) or isinstance(value, float):
        return value
    
    try:
        value = str(value)
        value = value.replace("$", "")
        value = value.replace(",", "")
        if value.find(".") == -1:
            retval = int(value)
        else:
            retval = float(value)
    except:
        if debug:
            print "Could not create numeric for:",value
        retval = None

    return retval
        


def fixName(name):
    if name:
        try:
            name   = name.decode('string_escape')
        except:
            name   = name
    return name



def nicerate(curval, lenval, size = None):
    curval = str(curval)
    lenval = str(lenval)
    while len(curval) < len(lenval):
        curval = " "+curval
    
    retval = " / ".join([curval, lenval])
    if size:
        return nice(retval, size)
    return retval



def nice(name, size):
    try:
        name = str(name)
    except:
        return name
    while len(name) < size:
        name += " "
    if name > size:
        name = name[:size]
    return name


def stripName(name):
    if name == None:
        return None
    if isinstance(name,str) or isinstance(name,unicode):
        if len(name) > 2:
            if name[:2] == "\n ":
                name = name[2:].strip()
            if name[-1] == "\n":
                name = name[:-1].strip()
    return name
    
                
def getSaveName(name, defval = "NoSaveName", maxval = 150):
    name = name.replace("/", "")
    name = name.replace("\"", "")
    name = name.replace("]", ")")
    name = name.replace("]", "(")
    while name[0] == ".":
        name = name[1:]
        if len(name) == 0:
            return defval
    if len(name) > maxval:
        name = name[:maxval]
    return name


def invertSaveName(name):
    name = name.replace(":", "/")
    return name
    
    

def makeCamelCase(val):
    vals = val.split()
    if len(vals) > 1:
        nval = [x.title() if len(x) > 2 else x for x in vals]
        return " ".join(nval)
    return val
    


def convertCurrency(val, debug = False):
    if debug: print "convertCurrency(",val,")"
    ogval = val
    
    if isinstance(val,str) or isinstance(val,unicode):
        if val.upper() == "N/A": return 0
        val = val.replace("$", "")
        val = val.replace(",", "")
    else:
        if debug: print "Returning",val,"because it is not an string/unicode"
        return val
    
    try:
        val = float(val)
    except:
        raise ValueError("Can not parse currency:",val,"from",ogval)
    
    return val    