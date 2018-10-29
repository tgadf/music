#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 11:14:17 2017

@author: tgadfort
"""

import hashlib
import sys
import itertools


###############################################################################
#
# Get Hash
#
###############################################################################
def getHashPermutations(rec, key = None, version = 2):
    vars=["account", "year", "month", "day", "amount"]
    mvars=[]
    if key == None:
        for mvar in itertools.permutations(vars, 5):
            mvars.append(mvar)
        return getHashVals(rec, mvars, version)
    
    knum = 0
    for mvar in itertools.permutations(vars, 5):
        if knum != key:
            knum += 1
            continue
        hashval = getHashVals(rec, [mvar], version)
        return hashval[0]


def getHashVals(rec, mvars, version):
    hashvals=[]
    for i in range(len(mvars)):
        m = hashlib.md5()
        vals=[]
        for var in mvars[i]:
            value=None
            if rec.get(var) != None:
                value=rec[var]
            elif rec.get(var.title()) != None:
                value=rec[var.title()]
            else:
                print rec
                raise ValueError("Could not find var:",var,"or",var.title(),"in",sys._getframe().f_code.co_name+"()")

            if version == 1:
                if var == "amount":
                    vals.append(str(float(value)))
                else:
                    vals.append(str(value))
            elif version == 2:
                if var == "amount":
                    vals.append("a"+str(round(float(value), 2)))
                elif var == "month":
                    vals.append("m"+str(value))
                elif var == "day":
                    vals.append("d"+str(value))
                elif var == "year":
                    vals.append("y"+str(value))
                else:
                    vals.append(str(value))
            else:
                raise ValueError("Hash version",version,"must be 1 or 2")
                
        #print i,vals
        for val in vals:
            m.update(val)
        hashvals.append(m.hexdigest())

    return hashvals



def getHash(rec, version = 2, key = None, quitOnError = True):
    #if rec.get('year') == None or rec.get('month') == None or rec.get('day') == None:
    #    return getHashDate(rec)
    #else:
    if rec.get('date') == None:
        raise ValueError("There is no date information in this record!")
    if rec.get('day') == None:
        raise ValueError("There is no day information in this record!")
    if rec.get('month') == None:
        raise ValueError("There is no month information in this record!")
    if rec.get('year') == None:
        raise ValueError("There is no year information in this record!")

    rec['amount'] = float(rec['amount'])
    
    if key == None and rec.get('key') != None:
        key = rec['key']
    
    return getHashPermutations(rec, key, version)



def checkHash(rec, hashval, quitOnError):
    recHash = getHash(rec=rec, key=rec.get('key'), quitOnError=quitOnError)
    if recHash != hashval:
        if quitOnError:
            raise ValueError("Record Hash:",recHash,"does not match other hash:",hashval)
        else:
            
            print "Record Hash:",recHash,"does not match other hash:",hashval
            return False
    return True