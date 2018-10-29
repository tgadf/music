import hashlib

##########################################
#
# Get Hash
#
##########################################
def getHash(rec):
    mvars={}
    mvars[0]=["account", "date", "amount"]
    mvars[1]=["account", "amount", "date"]
    mvars[2]=["date", "account", "amount"]
    mvars[3]=["date", "amount", "account"]
    mvars[4]=["amount", "account", "date"]
    mvars[5]=["amount", "date", "account"]

    hashvals=[]
    for i in range(6):
        m = hashlib.md5()
        vals=[]
        for var in mvars[i]:
            value=None
            if rec.get(var) != None:
                value=rec[var]
            elif rec.get(var.title()) != None:
                value=rec[var.title()]
            else:
                print "Could not find var:",var,"or",var.title(),"in",sys._getframe().f_code.co_name+"()"
                print rec
                exit()
            if var == "amount":
                vals.append(str(float(value)))
            else:
                vals.append(str(value))
        for val in vals:
            m.update(val)
        hashvals.append(m.hexdigest())

    return hashvals
