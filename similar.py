import csv
import utils
import bisect
try:
    import xbmc
except:
    pass

mainIds = ["imdb", "tmdb", "tvdb"]

def log(s, level = xbmc.LOGWARNING):
    utils.log(s,level)
    
def getUniqueIds(s, imdbLinks):
    #if "tt" in s:
    #    imdb = s.replace("tt","")                
    #    tmdb = bisect.bisect_left(imdbLinks, imdb) #[item[1] for item in imdbLinks if item[0] == imdb]
    #elif "tmdb" in s:
    #    tmdb = s.replace("tmdb","")
    #    imdb = [item[0] for item in imdbLinks if item[1] == tmdb]
    #    try:
    #        imdb = imdb[0]
    #    except:
    #        imdb = []
    #else:
    #    raise Exception("Unsupported unique id")
    
    ids = s.split("_")
    
    dic = {}
    for item in ids:
        for testId in mainIds:
            if testId in item:
                dic[testId] = item.replace(testId, "")
    
    if "imdb" in dic and "tmdb" in dic:
        utils.log("Both ids found. Fine")
    elif "imdb" in dic and not "tmdb" in dic:
        dic["tmdb"] = utils.getTmdbFromImdb(dic["imdb"])
    elif not "imdb" in dic and "tmdb" in dic:
        dic["imdb"] = utils.getImdbFromTmdb(dic["tmdb"])
    else:
        raise Exception("Not able to get tmdb id")
            
    tmdb = dic["tmdb"]    
    imdb = dic["imdb"]
        
    utils.log("Found Similar Filter: IMDB="+str(imdb)+" TMDB="+str(tmdb)+". " )
    return (imdb, tmdb)


def loadSimilarVideoDb(path):
    with open(path+'/imdb_links.csv') as csvfile:
        imdbLinks = list(csv.reader(csvfile, delimiter=',',))
            
    with open(path+'/imdb_sim.csv') as csvfile:
        imdbSim = list(csv.reader(csvfile, delimiter=',',))
        
    return (imdbLinks, imdbSim)
 

     
def convertTmdbToImdb(tmdbs):
    result = []
    for tmdb in tmdbs:
        x = utils.getImdbFromTmdb(tmdb)
        log(x)
        result.append(x)
    return result
        
    
    
def loadSimilarVideo_local(imdb, tmdb, imdbSim):
    #find similar movies as imdbs         
    imdbs = [item for item in imdbSim if item[0] == imdb]
    return imdbs
    
    
def hasMatch(video, movielist, idType):
    if idType in video['uniqueid']:
        try:
            if  int(video['uniqueid'][idType].replace("tt","")) in movielist:
                return True
        except:
            pass
    return False
    
def filterSimilarVideos(path, params, videos):
    
    (imdbLinks, imdbSim) = loadSimilarVideoDb(path)
    
    for item in params['category'].split(','):
        if '__SimilarTo__' in item:
            s = item.replace("__SimilarTo__", "")
             
            (imdb, tmdb) = getUniqueIds(s, imdbLinks)
            
            tmdbs = utils.loadSimilarVideo_tmdb(tmdb)
            log("Found Similar idxs TMDB"+str(tmdbs) ,level=xbmc.LOGWARNING)
               
            
            imdbs = convertTmdbToImdb(tmdbs)
            log("Found Similar idxs IMDB"+str(imdbs) ,level=xbmc.LOGWARNING)
            
            
            newvideos = []
            for video in videos:                
                if hasMatch(video, imdbs, "imdb") or hasMatch(video, tmdbs, "tmdb"): 
                    newvideos.append(video)                
                    
    log(newvideos)            
    
    return newvideos
        
        
if __name__ == "__main__":
    loadSimilarVideo_tmdb("27205")