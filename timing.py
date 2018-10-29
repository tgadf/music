#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 12:19:14 2017

@author: tgadfort
"""

from time import time
from strops import nicerate

def start():
    return time()

def inter(start, n, N = None):
    if n <= 0: return
    
    dT = time() - start
    
    if N:
        estTime = dT * N / float(n)
        remTime = estTime - dT
        print "  Processed",nicerate(n,N),"entries in",round(dT,1),"s. Remaining Time:",round(remTime,1),"s."
    else:
        print "  Processed",n,"entries in",round(dT,1),"s."    

def end(startval):
    print "Total Time:",int(time() - startval),"s."    