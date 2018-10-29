# !/usr/bin/python

import os
from mutagen.id3 import ID3, TYER
from mutagen.easyid3 import EasyID3

def checkMp3(name):
    audio = EasyID3(name)
    try:
        tracknumber = audio['tracknumber'][0]
        title       = audio['title'][0]
        album       = audio['album'][0]
        print tracknumber,' \t ',title,' \t ',album,' \t ',name
        if len(tracknumber) >= 1 and len(title) > 1 and len(album) > 1:
            return 1
        if len(tracknumber) >= 1 and len(title) > 1:
            return 2
        if len(tracknumber) >= 1:
            return 3
    except:
        print "No tracknumber."
        return 4


    return 5

#6-7-2010
#6-4-2010
#6-8-2010


copies = []
for root, dirs, files in os.walk(".", topdown=False):
    if root.find("dmb2010-") == -1:
        continue
    nmp3=0
    print ''
    vals = []
    for ifile in files:
        if nmp3 > 1: break
        ext = ifile[-4:]
        if ext == ".mp3":
            vals.append(checkMp3(os.path.join(root,ifile)))
            nmp3 += 1
    print "====>",vals,"<===="
    try:
        if vals[0] == 2 and vals[1] == 2:
            copies.append(root)
    except:
        x=1

    print "Copies:"
    for copy in copies:
        print copy
