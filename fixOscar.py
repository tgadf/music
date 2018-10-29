# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 14:02:09 2017

@author: tgadfort
"""

from os import mkdir
from os.path import join, splitext, basename
from Discog import fileops, yamldata, match
from collections import Counter, OrderedDict
from shutil import move
from glob import glob



def fix(name, outdir = "/Users/tgadfort/Movies/oscars/indiv", doit=False):
    ifile = join(outdir, name+".yaml")
    fdata = yamldata.getYaml(ifile)
    ndata = {}
    
    for year,ydata in fdata.iteritems():
        print year
        print "\t",ydata["Winner"]
        print "\t",ydata["Nominees"]
        
        if doit:
            if isinstance(ydata["Winner"], list):
                ydata["Winner"] = ydata["Winner"][0]
            for i,nominee in enumerate(ydata["Nominees"]):
                if isinstance(ydata["Nominees"][i], list):
                    ydata["Nominees"][i] = ydata["Nominees"][i][0]

        ndata[year] = ydata

    if doit:
        savefile = ifile.replace("/indiv", "/fix")
        yamldata.saveYaml(savefile, ndata)
        dst = ifile.replace("/indiv", "/old")
        move(ifile, dst)
        
        
def combine(indir = "/Users/tgadfort/Movies/oscars/fix"):
    fdata = {}
    for ifile in glob(join(indir, "*.yaml")):
        category = splitext(basename(ifile))[0]
        idata = yamldata.getYaml(ifile)
        for year,ydata in idata.iteritems():
            if fdata.get(year) == None:
                fdata[year] = {}
            if fdata[year].get(category) == None:
                fdata[year][category] = ydata
 
    outdir = "/Users/tgadfort/Movies/oscars"
    yamldata.saveYaml(join(outdir, "oscars.fix.yaml"), fdata)
           
        
        
        
def split():
    outdir = "/Users/tgadfort/Movies/oscars"
    cntr = Counter()
    data = yamldata.getYaml(join(outdir, "oscars.yaml"))
    fdata = {}
    for year,ydata in data.iteritems():
        for category,categorydata in ydata.iteritems():
            cntr[category] += 1
            if fdata.get(category) == None:
                fdata[category] = OrderedDict()
            fdata[category][year] = categorydata
            
            continue
            if category == "Best Motion Picture" or True:
                winner = categorydata.get("Winner")
                if isinstance(winner, list):
                    cntr[winner[0]] += 1
                else:
                    continue
                    cntr[winner] += 1
                continue
                nominees = categorydata.get("Nominees")
                for nominee in nominees:
                    if isinstance(nominee, list):
                        cntr[nominee[0]] += 1
                    else:
                        cntr[nominee] += 1
    
    
    savedir = join(outdir, "indiv")
    mkdir(savedir)
    for k,v in fdata.iteritems():
        savename = join(savedir, k+".yaml")
        print savename
        yamldata.saveYaml(savename, v)