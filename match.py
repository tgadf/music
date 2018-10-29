# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 15:23:08 2017

@author: tgadfort
"""
from difflib import get_close_matches

def findNearest(item, ilist, num, cutoff):
    nearest = get_close_matches(item, ilist, n=num, cutoff=cutoff)
    return nearest


def findMatchingWord(item, ilist, num=None, cutoff=None):
    nearest = [x for x in ilist if x.find(item) != -1]
    return nearest
