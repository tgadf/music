# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 22:02:56 2017

@author: tgadfort
"""

from datetime import date, datetime, timedelta
from time import strptime, strftime, struct_time
from dateutil.relativedelta import relativedelta
from calendar import monthrange


###############################################################################
#
# Get Timeline 
#
###############################################################################
def parseDate(strdate, guess = None, quitOnError = True, returnDate = True):
    
    if isinstance(strdate, date):
        if returnDate:
            return strdate
        else:
            return strdate.timetuple()

    if isinstance(strdate, struct_time):
        if returnDate:
            y,m,d = getYMD(strdate)
            dretval = date(y, m, d)
            return dretval
        else:
            return strdate

    
    seps    = ["/", "-", ".", " "]
    guesses = []
    if guess: guesses.append(guess)
    for sep in seps:
        guesses.append("%m"+sep+"%d"+sep+"%Y")
        guesses.append("%m"+sep+"%d"+sep+"%y")
        guesses.append("%Y"+sep+"%m"+sep+"%d")
        
    guesses.append("%b %d, %Y")
    guesses.append("%d %b, %Y")
        
    for guess in guesses:
        try:
            retval  = strptime(strdate, guess)
        except:
            continue

        if returnDate:
            y,m,d = getYMD(retval)
            dretval = date(y, m, d)
            return dretval
        else:
            return retval


    if quitOnError:
        raise ValueError("Could not parse date:",strdate)
        
    return None



def parseDateWithoutYear(strdate, year, guess = None, quitOnError = True, returnDate = True):
    if guess == None:
        guess = '%a, %b %d'
    try:
        retval  = strptime(strdate, guess)
    except:
        retval  = None
    
    if retval == None:
        strdate = strdate.replace("Sept ", "Sep ")
        try:
            retval = strptime(strdate, guess)
        except:
            retval = None

    if retval:
        m,d = retval.tm_mon,retval.tm_mday
        dretval = date(year, m, d)
        return writeDate(dretval)
    
    return None

        

def writeDate(dateval, dformat = "%m/%d/%Y"):
    if isinstance(dateval, date):
        tdate = parseDate(dateval, returnDate = False)
        return strftime(dformat, tdate)

    if isinstance(dateval, struct_time):
        return strftime(dformat, dateval)
    
    if isinstance(dateval, str) or isinstance(dateval, unicode):
        tdate = parseDate(dateval, returnDate = False)
        return strftime(dformat, tdate)

    raise ValueError("Could not get date because date is of type:",type(dateval))


def getDateValues(datevals):
    if isinstance(datevals, list):
        month = datevals[0]
        day   = datevals[1]
        year  = datevals[2]
    elif isinstance(datevals, struct_time):
        year  = datevals.tm_year
        month = datevals.tm_mon
        day   = datevals.tm_mday
    elif isinstance(datevals, date):
        year  = datevals.year
        month = datevals.month
        day   = datevals.day        
    elif isinstance(datevals, str) or isinstance(datevals, unicode):
        datevals = parseDate(datevals)
        year  = datevals.year
        month = datevals.month
        day   = datevals.day        
    else:
        raise ValueError("Not sure how to parse:",datevals,"of type:",type(datevals))

    return day,month,year


def createDMYDate(d, m, y):
    dval = date(y, m, d)
    return getDate(dval)

def getDMY(datevals):
    vals = getDateValues(datevals)
    return vals[0],vals[1],vals[2]

def createMDYDate(m, d, y):
    dval = date(y, m, d)
    return getDate(dval)

def getMDY(datevals):
    vals = getDateValues(datevals)
    return vals[1],vals[0],vals[2]

def createYMDDate(y, m, d):
    dval = date(y, m, d)
    return getDate(dval)

def getYMD(datevals):
    vals = getDateValues(datevals)
    return vals[2],vals[1],vals[0]



def getDate(value, guess = None, quitOnError = True):
    dateval = parseDate(value, guess, quitOnError)
    if dateval:
        return writeDate(dateval)
    else:
        if quitOnError:
            print "Could not get date from:",value
            raise()
            
    return None
        

def getNearbyDates(dateval, sigma):
    tdate = parseDate(dateval)
    dates = getDateRange(getdtime(tdate, -1*sigma), getdtime(tdate, sigma))
    if len(dates) > 2:
        dates = [dates[0], dates[-1]]
    return dates


def getLastDay(year, month, returnDate = False):
    try:
        year = int(year)
        month = int(month)
    except:
        raise ValueError("Year and month are not integers:",year,month)
    
    try:
        lastDay = monthrange(year, month)[1]
    except:
        raise ValueError("Could not get last day from year/month:",year,month)
        
    try:
        idate = createDMYDate(lastDay, month, year)
    except:
        raise ValueError("Could not create date from year/month/day:",year,month, lastDay)
        
    if returnDate:
        return idate
    else:
        return lastDay



##########################################
#
# Get dates between range
#
##########################################
def countDays(start_date, end_date, makeABS=False):
    startDate = parseDate(start_date, returnDate=True)
    endDate   = parseDate(end_date, returnDate=True)
    value = int((endDate - startDate).days)
    if makeABS:
        value = abs(value)
    return value

def dateGenRange(startDate, endDate):
    for n in range(countDays(startDate, endDate)):
        yield startDate + timedelta(n)

def getDateRange(start_date, end_date, returnGen = False):
    startDate = parseDate(start_date, returnDate=True)
    endDate   = parseDate(end_date, returnDate=True)
    
    if returnGen:
        return dateGenRange(startDate, endDate)
    else:
        dates = []
        for n in range(countDays(startDate, endDate)):
            dates.append(startDate + timedelta(n))
        return dates



##########################################
#
# Get months between range
#
##########################################
def getMinMaxStatements(statements):
    minDate = None
    maxDate = None
    for statement in statements:
        year,month = statement.split("-")
        idate = getLastDay(year, month, returnDate = True)        
        if minDate == None or maxDate == None:
            minDate = idate
            maxDate = idate
        if idate < minDate:
            minDate = idate
        if idate > maxDate:
            maxDate = idate
    return minDate,maxDate


def countMonths(start_date, end_date, makeABS=True):
    startDate = parseDate(start_date, returnDate=True)
    endDate   = parseDate(end_date, returnDate=True)
    value     = relativedelta(startDate, endDate).months
    if makeABS:
        value = abs(value)
    return value
    


##########################################
#
# Get years between range
#
##########################################
def countYears(start_date, end_date, makeABS=True):
    startDate = parseDate(start_date, returnDate=True)
    endDate   = parseDate(end_date, returnDate=True)
    value     = relativedelta(startDate, endDate).years
    if makeABS:
        value = abs(value)
    return value
    


##########################################
#
# Get/Parse date
#
##########################################
def getdtime(dateval, offset = None):
    tdate = parseDate(dateval, returnDate=True)
    if offset:
        tdate = tdate + relativedelta(days = offset)
    return tdate


def getYearMonth(dateval):
    dval = parseDate(dateval)
    return writeDate(dval, dformat="%Y-%m")


def getYear(idate):
    tdate = parseDate(idate)
    return tdate.year


def getWeek(idate):
    tdate = parseDate(idate)
    return tdate.isocalendar()[1]


def getYearDates(idate, returnDates=False):
    year = getYear(idate)
    vals = ["/".join(['1','1',str(year)]), "/".join(['12','31',str(year)])]
    if returnDates:
        vals = [parseDate(x) for x in vals]
    return vals



###############################################################################
#
# Check if date matches
#
###############################################################################
def matchDate(idate, testDate, returnDays = False):
    if parseDate(idate) == parseDate(testDate):
        if returnDays:
            return 0
        else:
            return True
    else:
        if returnDays:
            return countDays(idate, testDate)
        else:
            return False


def matchDateRange(idate, testDates):
    tdate = parseDate(idate)
    
    if isinstance(testDates, list):
        if len(testDates) == 2:
            startDate = parseDate(testDates[0])
            endDate   = parseDate(testDates[1])
        else:
            raise ValueError("TestDates must have two entres if a list",testDates)
    else:
        startDate = parseDate(testDates)
        endDate   = startDate

    if tdate >= startDate and tdate <= endDate:
        return True
    else:
        return False



###############################################################################
#
# Get Start/End Date From Dates
#
###############################################################################
def getDateText(startdate, enddate):
    start=[]
    start.append(startdate.year)
    start.append(startdate.month)
    start.append(startdate.day)
    end=[]
    if startdate.year == enddate.year:
        if startdate.month == enddate.month:
            end.append(enddate.day)
        else:
            end.append(enddate.month)
            end.append(enddate.day)
    else:
        end.append(enddate.year)
        end.append(enddate.month)
        end.append(enddate.day)
        
    start=[str(x) for x in start]
    startval=".".join(start)
    end=[str(x) for x in end]
    endval=".".join(end)
    return startval+"--"+endval



###############################################################################
#
# Get Timeline from records
#
###############################################################################
def getTimeline(data, quitOnError = True):
    start    = None
    end      = None
    timedata = []
    if isinstance(data, list):
        timedata.append(data)
    elif isinstance(data, dict):
        tdata=[]
        for k,v in data.iteritems():
            tdata.append(v)
        timedata.append(tdata)

    for tdata in timedata:
        if not isinstance(tdata, list): continue
        for val in tdata:
            dateval=val.get('date')
            if dateval == None:
                dateval=val.get('Date')
            if dateval == None:
                if quitOnError:
                    print val
                    raise ValueError("No date information in getTimeline()!!!")
                else:
                    continue
            
            tdate = parseDate(dateval)
            mon,day,year = getMDY(tdate)
            if year < 2000:
                print date
                raise()
            dtime=datetime( year, mon, day )
            if start == None or end == None:
                start = dtime
                end = dtime
            else:
                if dtime < start:
                    start = dtime
                if dtime > end:
                    end = dtime


    if start == None or end == None:
        print "Size of data:",len(data)
        if quitOnError:
            raise ValueError("No timeline information in data!")
        else:
            print "No timeline information in data!"
            print "Returning None,None from getTimeline()!!!"
            return None,None
    return start,end

