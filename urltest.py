# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 17:28:21 2017

@author: tgadfort
"""

import urllib2

url="https://www.discogs.com/artist/2428485-Хурд?sort=year%2Casc&limit=500&page=1"

req = urllib2.Request(url)
response = urllib2.urlopen(req)
print response
the_page = response.read()
print the_page