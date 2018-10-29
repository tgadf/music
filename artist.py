# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 15:45:48 2017

@author: tgadfort
"""

def getArtistSaveName(name):
    name = name.replace("/", ":")
    while name[0] == ".":
        name = name[1:]
        if len(name) == 0:
            return "NoArtistSaveName"            

def getArtistDiscID(suburl):
    ival = "/artist"
    pos = suburl.find(ival)
    if pos == -1:
        print "Could not find discID in", suburl
        raise()
    data = suburl[pos+len(ival)+1:]
    pos  = data.find("-")
    discID = data[:pos]
    try:
        int(discID)
    except:
        print "DiscID is not an integer",discID
        raise()
    
    return str(discID)