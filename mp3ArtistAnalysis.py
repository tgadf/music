#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 19:36:32 2017

@author: tgadfort
"""


import sys
if '/Users/tgadfort/Python' not in sys.path:
    sys.path.insert(0, '/Users/tgadfort/Python')

def knownSkips(artistName):
    known = []
    known.append("Elvis Costello & The Attractions")
    known.append("Elvis Costello & The Imposters")
    #known.append("Frankie Valli & The Four Seasons")
    #known.append("Frankie Valli & The Four Seasons*")
    known.append("Frankie Valley & The Travelers")
    known.append("Frankie Valli & The Romans")
    known.append("Rodgers & Hart")
    known.append("Simon & Garfunkel")
    known.append("Ronnie & The Pomona Casuals")
    known.append("Roy Loney & the Phantom Movers")
    known.append("Hootie & The Blowfish")
    known.append("DM Bob & The Deficits")
    known.append("Mike & The Mechanics")
    known.append("The Dave & Deke Combo")
    known.append("Joan Jett & The Blackhearts")
    known.append("Billy Dixon & The Topics")
    known.append("June & The Exit Wounds")
    known.append("Billy Gibbons & The Blue Union")
    known.append("Gary Lewis & The Playboys")
    known.append("Bruce Springsteen & The E-Street Band")
    known.append("Dodo & The Dodos")
    known.append("Huey Lewis & The News")
    known.append("KC & The Sunshine Band")
    known.append("Bob Seger & The Silver Bullet Band")
    known.append("Echo & The Bunnymen")
    known.append("Béla Fleck & The Flecktones")
    known.append("Ron Hagen & Pascal M.")
    known.append("Beavis & Butthead")
    known.append("Miss Tammy Faye Starlite & The Angels Of Mercy")
    known.append("Kool & The Gang")
    known.append("Dick Dale & His Del-Tones")
    known.append("Brooks & Dunn")
    known.append("Edie Brickell & New Bohemians")
    known.append("Ink & Dagger")
    known.append("Billy Bacon & The Forbidden Pigs")
    known.append("Charlie Waller & The Country Gentlemen")
    known.append("Rodgers & Hammerstein")
    known.append("Big & Rich")
    known.append("Jon Wahl & The Amadans")
    known.append("Steve Westfield & The Burnouts")
    known.append("Junior Walker & The All Stars")
    known.append("The Mamas & The Papas")
    known.append("Duke Ellington & His Orchestra")
    known.append("Kool & The Gang")
    known.append("Lissat & Brain")
    known.append("Steve Westfield & The Slow Band")
    #known.append("Charlie Waller & The Country Gentlemen")
    known.append("Ko & The Knockouts")
    known.append("Seals & Crofts")
    known.append("Cowboy & Spin Girl")
    known.append("Joe & Eddie")
    known.append("Hank Ballard & The Midnighters")
    known.append("Isaac Green & The Skalars")
    known.append("Nikki & The Corvettes")
    known.append("Abbott & Costello")
    known.append("Derek & The Dominos")
    known.append("Hall & Oates")
    known.append("Sonny & Cher")
    known.append("Dave Myers & The Surftones")
    known.append("Miss Tammy Faye Starlite & The Angels Of Mercy")
    known.append("DJ Jazzy Jeff & The Fresh Prince")
    known.append("Booker T & The MG's")
    known.append("Fred & The New J.B.'s")
    known.append("Ronnie & The Pomona Casuals")
    known.append("Daryl Hall & John Oates")
    known.append("Ronnie & The Pomona Casuals")
    known.append("Sir Bald Diddley & His Wig Outs")
    known.append("Steve Westfield & The Slow Band")
    #known.append("Al Dollar & His Ten Cent Band")
    known.append("Tee & Thee Crumpets")
    known.append("Red & The Red Hots")
    known.append("Belle & Sebastian")
    known.append("Jon Wahl & The Amadans")
    known.append("Jam & Spoon")
    known.append("Jan & Dean")
    known.append("Jim & Jesse")
    known.append("Phats & Small")
    known.append("Harvey & The Moonglows")
    known.append("Wild & Blue")
    known.append("Mark Johnson & Clawgrass")
    known.append("Big Brother & The Holding Company")
    known.append("Monrad & Rislund")
    known.append("Steve Westfield & The Slow Band")
    known.append("Pinkard & Bowden")
    known.append("Y & T")
    known.append("Jon Wahl & The Amadans")
    known.append("Rom & Comix")
    known.append("Lerner & Loewe")
    known.append("Fire & Ice")
    known.append("Sir Bald Diddley & His Wig-Outs")

    known.append("Certainly, Sir")
    known.append("Paris, Texas")
    known.append("Dearest, Crown")
    known.append("The Old, Old Story")
    known.append("Earth, Wind & Fire")
    known.append("Harry Connick, Jr.")
    known.append("Peter, Paul & Mary")
    known.append("Crosby, Stills, Nash & Young")
    known.append("Crosby, Stills & Nash")
    known.append("Shallow, North Dakota")
    known.append("10,000 Maniacs")
    known.append("Lambert, Hendricks & Ross")
    
    
    #vals = [x for x in discogArtists if x.find(" & ") != -1]
    #for val in vals:
    #    print "    known.append(\""+val+"\")"
    if artistName in known:
        return artistName
    return None


def noDiscogEntry(artistName):
    ## Known, but no Discogs
    noDiscogs = []
    noDiscogs.append("Marvy Darling")
    noDiscogs.append("Frank Fanelli")
    noDiscogs.append("Zoediac")
    noDiscogs.append("Fetish Doll")
    noDiscogs.append("Maino")
    noDiscogs.append("Capital 2")
    noDiscogs.append("Unknown Artist")
    noDiscogs.append("Various Artists")
    noDiscogs.append("Chinese Assassin")
    noDiscogs.append("Barry Kleinbort")
    noDiscogs.append("Beam & Yanou")
    noDiscogs.append("N.W.H.")
    noDiscogs.append("SD")
    noDiscogs.append("Zack Kekona")
    noDiscogs.append("Roots Rock Action Figures")
    noDiscogs.append("DJ E Stacks")
    noDiscogs.append("DJ OP")
    noDiscogs.append("Ryan California")
    noDiscogs.append("Melanie Sparks")
    noDiscogs.append("Morrie Schwartz")
    noDiscogs.append("DJ 2Mello")
    noDiscogs.append("Grand Master P")
    noDiscogs.append("The Old World")
    noDiscogs.append("Bob And Dana Kogut")
    noDiscogs.append("Cameron Silver")
    noDiscogs.append("Kristin Banks")
    noDiscogs.append("La Profecy")
    noDiscogs.append("Juice Escobar")
    noDiscogs.append("Moe Waveyy")
    noDiscogs.append("Mark Johnson & Clawgrass")
    noDiscogs.append("Gabe Nieto")
    noDiscogs.append("Heritage")
    noDiscogs.append("Spe$h")
    noDiscogs.append("Cosmic Free Way")
    noDiscogs.append("Lore Sjöberg And The Brunching Shuttlecocks")
    noDiscogs.append("The Intonations")
    noDiscogs.append("Dearest, Crown")
    noDiscogs.append("United Schach Corporation")
    noDiscogs.append("DJ Smooth Montana")
    noDiscogs.append("Tazzino")
    noDiscogs.append("DJ Aubrey")
    noDiscogs.append("DJ Mallin")
    noDiscogs.append("DJ Jeff Overstreet")
    noDiscogs.append("DJ Asad")
    noDiscogs.append("DJ Mellz")
    noDiscogs.append("DJ D-New")
    noDiscogs.append("DJ Purfiya")
    noDiscogs.append("DJ S.Whit")
    noDiscogs.append("DJ Hollygrove")
    noDiscogs.append("DJ Wispas")
    noDiscogs.append("DJ Ariel Assault")
    noDiscogs.append("DJ Twizt")
    noDiscogs.append("DJ Eggnie")
    noDiscogs.append("DJ Wintech")
    noDiscogs.append("DJ L-Straight")
    noDiscogs.append("DJ Scrill")
    noDiscogs.append("DJ ExMen")
    noDiscogs.append("DJ Cyber Trance")
    noDiscogs.append("DJ D.A.")
    noDiscogs.append("DJ Jean Live Mix")
    noDiscogs.append("DJ Gogy")
    noDiscogs.append("DJ P-Cutta")
    noDiscogs.append("DJ Big Tobacco")
    noDiscogs.append("Donovan Duke")
    noDiscogs.append("Mitch Harrell")
    noDiscogs.append("Blue Sky Frequency")
    noDiscogs.append("Candace Agree")
    noDiscogs.append("Punkemon")
    noDiscogs.append("Beaver Creek")
    noDiscogs.append("Jimmy Da Gent")
    noDiscogs.append("The Smokejumpers")
    noDiscogs.append("Fair River Station")
    noDiscogs.append("Trenchtown Rock")
    noDiscogs.append("Track Interpret")
    noDiscogs.append("Freightwhaler")
    noDiscogs.append("Philly Chase")
    noDiscogs.append("Koda Kumi")
    noDiscogs.append("Ian Boom")
    noDiscogs.append("Bizarre Sex Trio")
    noDiscogs.append("Cailey Ervin")
    noDiscogs.append("Trenzer")
    noDiscogs.append("The Coke Boys")
    noDiscogs.append("You")
    noDiscogs.append("Frank Lini")
    noDiscogs.append("Beatsnblends")
    noDiscogs.append("Hans Olav Slettebø")
    
    ## No idea
    noDiscogs.append("Midnight Highway")
    noDiscogs.append("Danichi")
    noDiscogs.append("3rd House")
    noDiscogs.append("Power Assume")
    noDiscogs.append("Gastr Del Hemp")
    noDiscogs.append("Uhmer")
    
    noDiscogs.append("Hustle Squad Dj's")
    noDiscogs.append("F.S.S. Stage Band")
    noDiscogs.append("Quang Tran")
    noDiscogs.append("Slow Band")
    noDiscogs.append("A Spanner In The Works")
    noDiscogs.append("Damn You Dave")
    noDiscogs.append("Dancehall Remixes")
    noDiscogs.append("Da Luniz")
    noDiscogs.append("The Old, Old Story")
    noDiscogs.append("Bogert")
    noDiscogs.append("DJEddieT.")
    noDiscogs.append("Coke Boy Brock")
    noDiscogs.append("Jon Wahl & The Amadans")
    noDiscogs.append("CutTime Players")
    noDiscogs.append("Eside Shawty")
    noDiscogs.append("Escape To Serentity")
    noDiscogs.append("Charlie Waller & The Country Gentlemen")
    noDiscogs.append("Kofi Baker Project")
    noDiscogs.append("The Velour Motel")
    noDiscogs.append("R!!!S!!!")
    noDiscogs.append("DJ COLETTE")
    noDiscogs.append("Waste Lagoon")
    noDiscogs.append("Din Fiv")
    noDiscogs.append("Gerrett G. Fagan")
    noDiscogs.append("Bipolar Outing")
    noDiscogs.append("TopDawgENT")
    noDiscogs.append("SS77(Strik)")
    noDiscogs.append("Dr. Tom Butt")
    noDiscogs.append("J-Kwon vs. Lil' Kim")
    noDiscogs.append("His Ten Cent Band")
    noDiscogs.append("DOTMOB")
    noDiscogs.append("I")
    noDiscogs.append("Interprètes Divers")
    noDiscogs.append("Die Feuer Rabe")
    noDiscogs.append("1世代")
    noDiscogs.append("tw 5")
    noDiscogs.append("Generic Blondes")
    noDiscogs.append("Squeaky Burger")
    noDiscogs.append("Count M'butu")
    noDiscogs.append("O.R.M ( Only Real Music )")
    noDiscogs.append("Skooda Chose")
    noDiscogs.append("Glo And Joe")
    noDiscogs.append("Hickory Tenpin")
    noDiscogs.append("Shooba Dooba")
    noDiscogs.append("Dundrennan")
    noDiscogs.append("Eclectics And Friends")
    noDiscogs.append("Please Visit")
    noDiscogs.append("Tribal Lust And The Horny Natives")
    noDiscogs.append("Robby Robott Band")
    noDiscogs.append("MoskaHouse")
    noDiscogs.append("Ymcmb")
    noDiscogs.append("Faure and Durufle Requiems")
    noDiscogs.append("Side Arm")
    noDiscogs.append("Daknit Bard Of Justice")
    noDiscogs.append("SlickF.B.")
    noDiscogs.append("NY C.E.O")
    noDiscogs.append("Pigs N' Ratts")
    noDiscogs.append("Az")
    noDiscogs.append("UT Pride of the Southland Marching Band")

    noDiscogs.append("Porn King")
    noDiscogs.append("Echoes Of Nature")
    noDiscogs.append("Rampal")
    noDiscogs.append("Dance Brothers")
    noDiscogs.append("Unknown")
    noDiscogs.append("Jim Breuer")  
    #noDiscogs.append("Anastasia")
    noDiscogs.append("Cyber-Tec")
    noDiscogs.append("Chris Con Carne")
    noDiscogs.append("Orbit 3")
    noDiscogs.append("Digital Overdrive")
    noDiscogs.append("Rom")
    noDiscogs.append("Kenny Chung")
    noDiscogs.append("Maceo")
    noDiscogs.append("Al Dollar")
    noDiscogs.append("Martk Cutler")
    noDiscogs.append("Dead Spot")
    noDiscogs.append("Screwston")


    if artistName in noDiscogs:
        return True
    return False


    

def splitMulti(artists):
    if artists == None:
        return None
    
    if isinstance(artists, list):
        retval = artists
    else:
        retval = []
        artists = [artists]

    retvals = []
    for artist in artists:
        retval = findMulti(artist)
        if retval:
            retvals += retval
        else:
            retvals.append(artist)
    return retvals


def findFeaturing(artistName):
    ## Determine if there is a feature artist
    primary   = None
    featuring = None
    splitVals = [" feat. ", " Feat. ", " Feat ", " Ft ", " ft "]
    for splitVal in splitVals:
        if featuring != None: break
        if artistName.find(splitVal) != -1:
            artists = artistName.split(splitVal)
            primary = artists[0].strip()
            featuring = artists[1:]    

    if featuring:
        featuring = splitMulti(featuring)
    return primary, featuring



def findSecondary(artistName):
    ## Determine if there is a secondary artist
    primary   = None
    secondary = None
    splitVals = [","]
    for splitVal in splitVals:
        if secondary != None: break
        if artistName.find(splitVal) != -1:
            artists   = artistName.split(splitVal)
            primary   = artists[0].strip()
            secondary = artists[1:]

    if secondary:
        secondary = splitMulti(secondary)

    return primary, secondary


def findMulti(artistName):
    ## Determine if there are multi artists
    multi   = None
    splitVals = [" & ", " vs. ", " vs "]
    for splitVal in splitVals:
        if artistName.find(splitVal) != -1:
            multi     = artistName.split(splitVal)
            break

    return multi



def findSongArtists(artistName, fileName = None):
    
    primary   = None
    secondary = None
    featuring = None
    multi     = None

    if primary == None:
        primary = knownSkips(artistName)
        
    if primary == None:
        primary, featuring = findFeaturing(artistName)
    
    if primary == None:
        primary, secondary = findSecondary(artistName)
    
    if primary == None:
        multi = findMulti(artistName)

    if not any([secondary, featuring, multi]):
        primary = artistName


        
    retval = {"Primary": primary, 
              "Featuring": featuring,
              "Secondary": secondary,
              "Multi": multi}
    return retval



def getArtists(songArtists, returnString = False):
    if not isinstance(songArtists, dict):
        return []
    
    artists = {}
    for k,v in songArtists.iteritems():
        if v:
            if isinstance(v, list):
                for artist in v:
                    artists[artist] = 1
            else:
                artists[v] = 1

    if returnString:
        return " & ".join(artists.keys())
    else:
        return artists.keys()