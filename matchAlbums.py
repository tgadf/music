from difflib import SequenceMatcher
from searchUtils import findNearest

class matchAlbums():
    def __init__(self, name="Dummy", n=1, cutoff=0.7):
        self.name      = name
        self.minAlbums = n
        self.cutoff    = cutoff

        self.exact   = None
        self.near    = None
        self.score   = None
        self.thresh  = None
        self.maxval  = None
        self.albums  = None
        self.nearest = None
        self.mapping = {}
        self.bestmap = {}
        
        
    def getBestMatch(self, album):
        return self.bestmap.get(album)
        
        
    def show(self, debug=False):
        print("Best Matches of\n\t[{0}]\n\t[{1}]\nAlbum Lists".format(self.albums[0], self.albums[1]))
        print("\tExact Matches:          {0}".format(self.exact))
        print("\tNear Matches:           {0}".format(self.near))
        print("\tMax Matches:            {0}".format(self.maxval))
        print("\tTotal Score:            {0}".format(self.score))
        print("\tScore/Albums:           {0}".format(round(self.score/len(self.albums[0]), 3)))
        print("\tThreshold Score:        {0}".format(self.thresh))
        print("\tBest Match:             {0}".format(self.bestmap))
        if self.near > 0:
            print("\tThreshold Score/Albums: {0}".format(round(self.thresh/self.near), 3))
        if debug:
            print("\tFull Mapping")
            for albumA, albumAmapping in self.mapping.items():
                print("\t  {0}".format(albumA))
                for albumB, ratio in albumAmapping.items():
                    print("\t\t{0: <30}{1}".format(albumB, ratio))
        
        
    def match(self, albums1, albums2, debug=False):
        if debug:
            print("\tFinding Best Matches of [{0}] and [{1}] Album Lists".format(len(albums1), len(albums2)))
            
        if albums1 is None:
            raise ValueError("1st set of albums is NULL! for {0}".format(self.name))
        if albums2 is None:
            raise ValueError("2nd set of albums is NULL! for {0}".format(self.name))


        albums2map = None
        if isinstance(albums2, dict):
            albums2map = {v: k for k, v in albums2.items()}
            albums2 = list(albums2.values())
        elif isinstance(albums2, list):
            pass
        else:
            raise ValueError("Albums to match type of [{0}] is unknown".format(type(albums2)))
            
        self.exact   = len(set(albums1).intersection(set(albums2)))
        self.near    = 0
        self.score   = 0.0
        self.thresh  = 0.0
        self.maxval  = 0.0
        self.albums  = [albums1, albums2]
        self.nearest = []
        self.bestmap = {}

        
        for albumA in albums1:
            self.bestmap[albumA] = None
            
            nearest = {"Album": None, "Ratio": 0.0}
            self.mapping[albumA] = {}
            for albumB in albums2:
                s     = SequenceMatcher(None, albumA, albumB)
                ratio = round(s.ratio(),3)
                self.mapping[albumA][albumB] = ratio
                if ratio > nearest["Ratio"]:
                    nearest = {"Album": albumB, "Ratio": ratio}
                    
            self.nearest.append(nearest)
            self.score += nearest["Ratio"]
            self.maxval = max([self.maxval, nearest["Ratio"]])
            if nearest["Ratio"] >= self.cutoff:
                self.near   += 1
                self.thresh += nearest["Ratio"]
                if albums2map is None:
                    self.bestmap[albumA] = {"Name": nearest["Album"], "Code": None}
                else:
                    self.bestmap[albumA] = {"Name": nearest["Album"], "Code": albums2map[nearest["Album"]]}
                
        
        self.score  = round(self.score,3)
        self.thresh = round(self.thresh,3)
        self.maxval = round(self.maxval,3)