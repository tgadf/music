#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 18:08:58 2017

@author: tgadfort
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 17:42:51 2017
 
@author: tgadfort
"""

import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

from download import getData
from htmlParser import getHTML
from fsio import isDir, getPath, mkSubDir, setFile, setSubFile, isFile

def getSongDBDir():
    if isDir("/Volumes/Music/songDB"):
        return getPath("/Volumes/Music/songDB")
    elif isDir("/Users/tgadfort/Documents/music/songDB"):
        return getPath("/Users/tgadfort/Documents/music/songDB")
    else:
        raise ValueError("No songDB dir")
        
 
def parseMainPage():
 
    ifile = setSubFile(getSongDBDir(), "data", "Billboard chart archive.html")
    if not isFile(ifile):
        raise ValueError("No",ifile)
    
    data = {}
    tblMap = {2: "Artists", 4: "Hot 100", 7: "Top 40", 10: "Alternative", 13: "Rock",
    16: "Country", 19: "Adult Contemporary", 22: "R&B/Hip-Hop", 25: "UK",
    28: "Best Sellers", 31: "Jukebox", 34: "Cash Box"}
 
    bsdata = getHTML(open(ifile))
    tables = bsdata.findAll("table")
    for i,table in enumerate(tables):
      trs = table.findAll("tr")
      for j,tr in enumerate(trs):
        tds = tr.findAll("td")
        for k,td in enumerate(tds):
          hrefs = td.findAll("a")
          for l,href in enumerate(hrefs):
           
            if tblMap.get(i):
              key = tblMap[i]
              if data.get(key) == None:
                data[key] = {}
              data[key][href.text] = href.attrs['href']
              #print data[key][href.text]
 
            print "/".join([str(i),str(len(tables))]),"\t",
            print "/".join([str(j),str(len(trs))]),"\t",
            print "/".join([str(k),str(len(tds))]),"\t",
            print "/".join([str(l),str(len(hrefs))]),"\t",
            print href.text
             
        print '\n'
      print "\n"

    return data
 
    

def downloadTopicPages(data, debug = True):
    dtime = 10
    useSafari = True
    for k,v in data.iteritems():
        topic = k
        print topic
        saveDir = mkSubDir(getSongDBDir(), ["data", topic])
        for year,topicref in v.iteritems():
            savename = setFile(saveDir, str(year)+".html")
            if isFile(savename):
                continue
            URL = "http://www.song-database.com/charts.php"+topicref
            print URL
            print "http://www.song-database.com/charts.php?wk=2003-00-00&type=ac"
            #getData(base=url, savename=savename, useSafari=False)
            retval = getData(base=URL, suburl=None, extra=None, savename=savename, 
                             useSafari=useSafari, dtime=dtime, debug=debug)
            f()
            sleep(5)
    
 
def parseTopicPages(ifile = "BillboardHot100.html"):
 
    data = {}
 
    bsdata = getHTML(open(ifile))
    tables = bsdata.findAll("table")
    for i,table in enumerate(tables):
      trs = table.findAll("tr")
      for j,tr in enumerate(trs):
        tds = tr.findAll("td")
        for k,td in enumerate(tds):
          if i == 3 and j == 0:
            bs = td.findAll("b")
            if len(bs) == 3:
              key = bs[1].text
            elif len(bs) == 2:
              key = bs[0].text
            else:
              raise ValueError("Not sure how to parse",bs)
          if i < 3 or i > 3:
            key = None
 
          hrefs = td.findAll("a")
          for l,href in enumerate(hrefs):   
 
            if key:
              if data.get(key) == None:
                data[key] = {}
              data[key][href.text] = href.attrs['href']
             
            print "/".join([str(i),str(len(tables))]),"\t",
            print "/".join([str(j),str(len(trs))]),"\t",
            print "/".join([str(k),str(len(tds))]),"\t",
            print "/".join([str(l),str(len(hrefs))]),"\t",
            print href.text
             
        print '\n'
      print "\n"
 
    print data 
 
 
def parseChartPages(ifile = "BillboardChart.html"):
 
    data = []
 
    bsdata = getHTML(open(ifile))
    tables = bsdata.findAll("table")
    for i,table in enumerate(tables):
      trs = table.findAll("tr")
      if i == 4:
        for j,tr in enumerate(trs):
          tds = tr.findAll("td")
          title = tds[4]
          artist = tds[5]
          peak = tds[8]
          weeks = tds[9]
          span = title.find("span")
          if span == None:
            continue
          if span:
            title = span.text
            print "==>",title,'\t\t',
          ref = artist.find("a")
          if ref:
            artist = ref.text
            ref = ref.attrs['href']
            print "==>",artist,'\t\t',
          pk = peak.text
          pk = pk.replace("&nbsp;", "")
          try:
            pk = int(pk)
          except:
            pk = None
         
          wk = weeks.text
          try:
            wk = int(wk)
          except:
            wk = None
           
          print "==>",pk,'\t',wk
         
          data.append({"Artist": artist, "Title": title, "Peak": pk, "Weeks": wk})
 
    return data 
 
 
data = parseMainPage()
downloadTopicPages(data)
#parseTopicPages()
#parseChartPages()