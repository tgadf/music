# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 21:15:08 2017

@author: tgadfort
"""

from re import match, search, findall, compile
import strdate

def splitMatch(matchval, album):
    name  = album.replace(matchval, "")
    isnew = name == album
    name  = name.split()
    return name,isnew
    

def stripName(name):
    pos = name.find("Live On")
    if pos < len(name)/3 and pos >= 0:
        name = name.replace("Live On")
    return name
    

def suggestedName(tdate, name):
    datestring = strdate.getDateString(tdate)
    retval = "Live on "+datestring+" at "+name
    return retval


def isKnownAlbumType(album):
    if album == None:
        return False
    known  = compile(r"Live on (\d+)-(\d+)-(\d+) at ")
    retval = known.search(album)
    if retval:
        return True
    return False


def getDateName(line):
    delims = [ x.replace(".", "\.") for x in ['-', '.', ' ', '_'] ]
    date   = None
    for delim in delims:
        date,pattern = strdate.findDate(line, delim)
        break
    if date == None:
        date,pattern = strdate.findDate(line, "")
        
    if date:
            name   = line.replace(pattern, "")
            name   = name.strip()
            name   = stripName(name)
            retval = suggestedName(date, name)
            print '[',date,']\t[',pattern,']\t[',name,']\t[',line,']'
            print "==>",retval
            return retval
            
    return None
        