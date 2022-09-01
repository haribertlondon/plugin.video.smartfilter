import utils
try:
    import xbmc
except:
    pass

mainIds = ["imdb", "tmdb", "tvdb","mediatype"]

   
def getTmdbId(s):
    ids = s.split("_")
    
    dic = {}
    for item in ids:
        for testId in mainIds:
            if testId in item:
                dic[testId] = item.replace(testId, "")
     
    if not "tmdb" in dic:
        if "imdb" in dic:
            dic["tmdb"] = utils.getTmdbFromImdb(dic["imdb"])
        
        if "tvdb" in dic:
            dic["tmdb"] = utils.getTmdbFromTvdb(dic["tvdb"])            
    
    mediatype = dic["mediatype"]
        
    try:    
        tmdb = dic["tmdb"]
    except Exception as e:
        raise Exception("getTmdbId: Not able to get tmdb id. String="+s+ "Error= "+str(e), level=xbmc.LOGWARNING)    
        
    utils.log("Found Similar Filter:  TMDB="+str(tmdb)+". " )
    return (tmdb, mediatype)


    
def getAllPlatformIds(tmdbs, mediatype):
    result = []
    for tmdb in tmdbs:
        platformIds = utils.getTvdbAndImdbFromTmdb(tmdb, mediatype) 
        
        result.append( platformIds )
    return result
        
    
    
def loadSimilarVideo_local(imdb, tmdb, imdbSim):
    #find similar movies as imdbs         
    imdbs = [item for item in imdbSim if item[0] == imdb]
    return imdbs
    
   
def hasMatch(video, similarIds):
    #utils.log("Checking: "+repr(video) +  repr(similarIds))
    
    for similarId in similarIds:
        for platformKey, platformId in list(similarId.items()):
            try:
                if int(video['uniqueid'][platformKey].replace("tt","")) == platformId:
                    utils.log("Found xxxx")
                    return True
            except Exception as e:
                utils.log('Exception: Has Match (similar)' + repr(e), level=xbmc.LOGWARNING)
                pass
        
    return False

def getSimilarVideos(params):
    isSeries = None
    platformIds = []
    if 'category' in params:
        for item in params['category'].split(','):
            if '__SimilarTo__' in item:
                s = item.replace("__SimilarTo__", "")
                 
                (tmdb, mediatype) = getTmdbId(s)
                
                if "tv" in mediatype or "episode" in mediatype or "season" in mediatype:
                    isSeries = True
                else:
                    isSeries = False
                
                tmdbs = utils.loadSimilarVideo_tmdb(tmdb, mediatype)
                utils.log("Found Similar idxs TMDB: "+repr(tmdbs))
                
                platformIds = getAllPlatformIds(tmdbs, mediatype)
                utils.log("Found Similar idxs on all platforms: "+repr(platformIds))
    return (platformIds, isSeries )
    
def filterSimilarVideos(params, videos, similarIds, keyword):
    newvideos = videos
    if 'category' in params:
        for item in params['category'].split(','):
            if keyword in item:
                newvideos = []
                for video in videos:                
                    if hasMatch(video, similarIds): 
                        newvideos.append(video)                
    return newvideos
        
        
if __name__ == "__main__":
    #loadSimilarVideo_tmdb("27205","movie")
    params = {"category": "__SimilarTo__tvdb95011_mediatypetvshow", }
    (platformIds, isSeries ) = getSimilarVideos(params)  
    filterSimilarVideos(params, [ {'uniqueid': {"tvdb": 1000 }}, {'uniqueid': {"imdb":"tt1000"}}, {'uniqueid': {"tmdb":1418}} ], platformIds)