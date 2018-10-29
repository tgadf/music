# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 19:29:29 2017

@author: tgadfort
"""

from mutagen.easyid3 import EasyID3

def setCompilation(mp3, compVal):
    try:
        audio = EasyID3(mp3)
        audio['compilation'] = compVal
        audio.save()
        print "Setting compilation to",compVal,"for",mp3
        return True
    except:
        print "Could not setting compilation to",compVal,"for",mp3
    return False


def getCompilation(audio):
    compVal = None
    try:
        if audio.get('compilation'): compVal = audio['compilation'][0]
    except:
        compVal = None
    return compVal


def setArtist(mp3, artist):
    try:
        audio = EasyID3(mp3)
        audio['artist'] = artist
        audio.save()
        print "Setting artist",artist,"to",mp3
        return True
    except:
        print "Could not save artist",artist,"to",mp3
    return False


def getArtist(audio):
    artist = None
    try:
        if audio.get('artist'): artist = audio['artist'][0]
    except:
        artist = None
    return artist


def setAlbum(mp3, album):
    try:
        audio = EasyID3(mp3)
        audio['album'] = album
        audio.save()
        print "Setting album",album,"to",mp3
        return True
    except:
        print "Could not save album",album,"to",mp3
    return False


def getAlbum(audio):
    album = None
    try:
        if audio.get('album'): album = audio['album'][0]
    except:
        album = None
    return album
    
    
def getTrackNo(audio):
    tracknumber = None
    try:
        if audio.get('tracknumber'): tracknumber = audio['tracknumber'][0]
    except:
        tracknumber = None
    return tracknumber
    

def getInfo(mp3):    
    try:
        audio = EasyID3(mp3)
    except:
        return None, None, None, None, None
    artist      = getArtist(audio)
    album       = getAlbum(audio)
    trackno     = getTrackNo(audio)
    compilation = getCompilation(audio)
    try:
        other   = zip(audio.keys(), audio.values())
    except:
        other   = None
    return artist, album, trackno, compilation, other
        
