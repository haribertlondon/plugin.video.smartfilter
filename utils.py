try:
    import xbmc
    import urllib2
    from urllib import urlencode
    from urlparse import parse_qsl
    import urllib2 as urlrequest #@UnresolvedImport @Reimport
except:
    import urllib.request as urlrequest #@UnusedImport

import ssl
import os
import json

apikey = "10dc4a6c0d1a5e1bb338c026d5e7e6f1"

def log(s, level=xbmc.LOGWARNING):
    try:
        xbmc.log( repr(s) ,level=level)
    except:
        print( repr(s) )
        

        
def loadSimilarVideo_tmdb(tmdbID):
    url = "https://api.themoviedb.org/3/movie/"+str(tmdbID)+"/recommendations?api_key="+apikey+"&language=de-DE&page=1"
    log(url)
    
    dic = getTMDB(url)
    
    tmdbs = []
    for i in dic['results']:
        tmdbs.append(i['id'])
    
    log(tmdbs)
       
    return tmdbs
    

def getTmdbFromImdb(imdb):
    try:
        imdb = imdb.replace("tt","")
        dic = getTMDB("https://api.themoviedb.org/3/find/tt"+imdb+"?api_key="+apikey+"&language=en-US&external_source=imdb_id")
        tmdb = dic["movie_results"][0]["id"]
    except Exception as e:
        log(e)
        tmdb = ""
    return tmdb

def getImdbFromTmdb(tmdb):
    try:
        dic = getTMDB("https://api.themoviedb.org/3/movie/"+str(tmdb)+"?api_key="+apikey+"&append_to_response=external_ids")
        imdb = int(dic["imdb_id"].replace("tt",""))
    except Exception as e:
        log(e)
        imdb = "error in getImdbFromTmdb"
    return imdb

def getTMDB(url):
    html = downloadBinary(url).decode('utf-8')
    
    log("HTML Result from TMDB: "+html,level=xbmc.LOGWARNING)
    
    dic = json.loads(html)
    log(dic)
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
