from string import ascii_uppercase, ascii_lowercase, digits

class primeDirectory:
    def __init__(self, debug=False):
        retvals  = [x for x in ascii_uppercase]
        retvals += ["Num", "Xtra", "The"]
        retvals  = sorted(retvals)
        self.primeDirectories = retvals

            
    def getPrimeDirectories(self):    
        return self.primeDirectories
    

    def getPrimeDirectory(self, artistName):
        try:
            start = artistName[0]
        except:
            raise ValueError("Prime Directory cannot be found for {0}".format(artistName))

        if start in ascii_uppercase:
            if artistName.startswith("The "):
                return "The"
            return start
        if start in ascii_lowercase:
            return "Xtra"
        elif start in digits:
            return "Num"
        else:
            return "Xtra"
            raise ValueError("Could not determine Prime Directory for Artist {0}".format(artistName))