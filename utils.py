try:
    import xbmc
    import urllib.request, urllib.error, urllib.parse
    from urllib.parse import urlencode
    from urllib.parse import parse_qsl
    import urllib2 as urlrequest #@UnresolvedImport @Reimport
except:
    import urllib.request as urlrequest #@UnusedImport

import cache
import ssl
import os
import json

apikey = "10dc4a6c0d1a5e1bb338c026d5e7e6f1"


def jsonKeys2int(x):
    if isinstance(x, dict):
        try:
            return {int(k):v for k,v in list(x.items())}
        except:
            return x
    else:
        return x

#movie helpers
def reduceMovie(movie):
    return dict((k, movie[k]) for k in ('label', 'uniqueid'))


def getTmdbID(movie):
    try:
        return int(movie["uniqueid"]["tmdb"])
    except:
        log("Error while accessing TMDB ID. " + repr(movie))

def compareMovies(movie1, movie2):
    return getTmdbID(movie1) == getTmdbID(movie2)

def getJSON(cachefile, url, select, cacheAge = 7):
    log("Try to get cached info..." )
    js = cache.getCache(cachefile, url, cacheAge, 'json')
    if js is None or len(js) == 0:
        xbmc.log("Nothing found in cache. Getting by JSON RPC ",level=xbmc.LOGWARNING)
        js = getJSON_direct(url, select)
        xbmc.log("Data received. Storing to cache",level=xbmc.LOGWARNING)
        cache.setCache(cachefile, url, js, 'json')
    return js
    
def getJSON_direct(url, select):
    html = ""    
    try:    
        html = xbmc.executeJSONRPC(url)
        log("getJSON_direct: "+html[:200])
        js = json.loads(html) #convert json -> dic        
        return js['result'][select]
    except Exception as e:        
        log('Syncplayer: Json Error: '+str(e) +' Url='+str(url) + ' Response' + str(html), level=xbmc.LOGWARNING)
        return {}


def log(s, level = xbmc.LOGDEBUG):
    output =  "Smartfilter: " + repr(s)
    try:
        xbmc.log(output ,level)
        #do nothing, only activate for debug
        pass
    except:
        print(( repr(output) ))
        

        
def loadSimilarVideo_tmdb(tmdbID, mediatype):
       
    url = "https://api.themoviedb.org/3/"+mediatype.replace("tvshow","tv")+"/"+str(tmdbID)+"/recommendations?api_key="+apikey+"&language=de-DE&page=1"    
    
    dic = getTMDB(url)
    tmdbs = []
    for i in dic['results']:
        tmdbs.append(i['id'])
       
    return tmdbs
    
def getTmdbFromTvdb(tvdb):
    try:
        dic = getTMDB("https://api.themoviedb.org/3/find/"+tvdb+"?api_key="+apikey+"&language=en-US&external_source=tvdb_id")
        tmdb = dic["tv_results"][0]["id"]
    except Exception as e:
        log(e)
        tmdb = ""
    return tmdb

def getTmdbFromImdb(imdb):
    try:
        imdb = imdb.replace("tt","")
        dic = getTMDB("https://api.themoviedb.org/3/find/tt"+imdb+"?api_key="+apikey+"&language=en-US&external_source=imdb_id")
        tmdb = dic["movie_results"][0]["id"]
    except Exception as e:
        log(e)
        tmdb = ""
    return tmdb

def getTvdbAndImdbFromTmdb(tmdb, mediatype):
    result = {} 
    try:
        #dic = getTMDB("https://api.themoviedb.org/3/"+mediatype.replace("tvshow","tv")+"/"+str(tmdb)+"?api_key="+apikey+"&append_to_response=external_ids")
        #ext = dic["external_ids"]
        result["tmdb"] = int(tmdb)
        #result["imdb"] = int(ext.get("imdb_id","0").replace("tt",""))
        #result["tvdb"] = int(ext.get("tvdb_id","0"))
    except Exception as e:
        log(e)
        
    return result

def getTMDB(url):
    log("HTML Request: "+url)
    html = downloadBinary(url).decode('utf-8')
    log("HTML Result: "+html[:200])
    dic = json.loads(html)
    log("getTMDB: "+repr(dic)[:200]+'...')
    return dic

apikey = apikey.replace("dc","cd")

def downloadBinary(url):
        
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)): 
        ssl._create_default_https_context = ssl._create_unverified_context
    
    try:
        req = urlrequest.Request(url)
        #req.add_header('Referer', 'http://www.python.org/')
        # Customize the default User-Agent header value:
        req.add_header('User-Agent', '')
        r = urlrequest.urlopen(req)
        html = r.read()
    except Exception as e:
        print(("Error with link "+url))
        print((str(e)))
        html = "" 
        
    return html
