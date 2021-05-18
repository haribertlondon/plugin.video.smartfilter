#import pickle
import logging
import datetime
import logUtils
import json
import pickle 

#json is faster than pickle

def save_obj(obj, filename, fileFormat):
    
    if fileFormat == 'json':
        with open(filename, 'w') as f:        
            json.dump(obj, f, default=str)
    else:
        with open(filename, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)          

def openCacheFile(filename, fileFormat = 'pickle'):
    try:        
        if fileFormat == 'json':
            with open(filename, 'r') as f:
                return json.load(f)
        else:
            with open(filename, 'rb') as f:
                return pickle.load(f)     
    except Exception as e:
        print(e)        
        logging.warning("Cache File <"+str(filename) + "> does not exist")        
        return {} #empty dictionary

def setCache(filename, key, content, fileFormat = 'pickle'):
    cache = openCacheFile(filename, fileFormat)
    now=datetime.datetime.now()
    cache[key] = (now, content)
    save_obj(cache, filename, fileFormat)

def checkDate(date, maxDays, fileFormat):
    now=datetime.datetime.now()
    if fileFormat == 'json':
        try: 
            date= datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        except:
            date= datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    dayDelta= (now - date).days
    if  dayDelta <= maxDays:
        return True
    else:
        logging.warning("Entry too old. " + str(dayDelta) + ">" + str(maxDays) + " Days")
        return False

def getCache(filename, key, maxDays, fileFormat = 'pickle'):

    if type(filename)== str:
        cache = openCacheFile(filename, fileFormat)    
    else:
        cache = filename
        
    if  key in cache:
        (date, content) = cache[key]
    else:
        logging.warning("Key <" + key + "> does not exist")
        return ""

    if checkDate(date, maxDays, fileFormat):
        return content
    else:   
        logging.warning("Key <" + key + "> found but too old: "+str(date))     
        return ""

def cleanCache(filename, maxDays, fileFormat = 'pickle'):
    cache = openCacheFile(filename, fileFormat)  
    newCache = {} #new dictionary
    
    for key, value in cache.items():
        (date, _) = value
        if checkDate(date, maxDays):
            newCache[key]=value
            
    save_obj(newCache, filename)
            

if __name__ == "__main__":
    #set logging options
    logUtils.setLogger('Z:/Programs/AutoOTR/getCache.log')

    #setCache("test.cache", "Pferd", "Hufe")
    #cleanCache("test.cache", 1)
    #x=getCache("test.cache", "Pferd", 1)
    
    

    #print(x)
