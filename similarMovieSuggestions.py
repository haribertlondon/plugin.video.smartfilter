'''
Created on 26.07.2022

@author: bmueller
'''
try:
    import xbmc
    import xbmcgui
except:
    pass
import io
import json
import utils

_maxSimilarPerMovie = 10

class similarMovieSuggestions:
    
    def __init__(self, cachefileDBCreation, cachefileRecent, databaseFile):
        self.cachefileDBCreation = cachefileDBCreation
        self.cachefileRecent = cachefileRecent
        self.databaseFile = databaseFile
    
    def get_similarity_score(self, ref_movie, other_movie, set_genres=None, set_directors=None,
                                                        set_writers=None, set_cast=None, set_tags=None):      
        # assign arguments not given
        if not set_genres:
            (set_genres, set_directors, set_writers, set_cast, set_tags ) = self.get_sets(ref_movie) 
        # calculate individual scores for contributing factors
        # [feature]_score = (numer of matching [features]) / (number of unique [features] between both)
        genre_score = float(len(set_genres.intersection(other_movie["genre"])))/ \
            len(set_genres.union(other_movie["genre"]))
        director_score = 0 if len(set_directors)==0 else \
            float(len(set_directors.intersection(other_movie["director"])))/ \
            len(set_directors.union(other_movie["director"]))
        writer_score = 0 if len(set_writers)==0 else \
            float(len(set_writers.intersection(other_movie["writer"])))/ \
            len(set_writers.union(other_movie["writer"]))
        tags_score = 0 if len(set_tags)==0 else \
            float(len(set_tags.intersection(other_movie["tag"])))/ \
            len(set_tags.union(other_movie["tag"]))
        # cast_score is normalized by fixed amount of 5, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection( [x["name"] for x in other_movie["cast"][:5]] )))/5)**(1./2)
        # rating_score is "closeness" in rating, scaled to 1 (0 if greater than 3)
        if ref_movie["rating"] and other_movie["rating"] and abs(ref_movie["rating"]-other_movie["rating"])<3:
            rating_score = 1-abs(ref_movie["rating"]-other_movie["rating"])/3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_movie["year"] and other_movie["year"] and abs(ref_movie["year"]-other_movie["year"])<10:
            year_score = 1-abs(ref_movie["year"]-other_movie["year"])/10
        else:
            year_score = 0
        # mpaa_score gets 1 if same mpaa rating, otherwise 0
        mpaa_score = 1 if ref_movie["mpaa"] and ref_movie["mpaa"]==other_movie["mpaa"] else 0
        # calculate overall score using weighted average
        similarscore = (.5*genre_score + .15*director_score + .125*writer_score + .05*cast_score + .075*rating_score + .075*year_score + .025*mpaa_score + .125*tags_score)/1.125
        # exponentially scale score for movies in same set
        if ref_movie["setid"] and ref_movie["setid"]==other_movie["setid"]:
            similarscore **= (1./2)
        return similarscore
     
    def get_sets(self, ref_movie):    
        set_genres = set(ref_movie["genre"])    
        set_directors = set(ref_movie["director"])    
        set_writers = set(ref_movie["writer"])    
        set_cast = set([x["name"] for x in ref_movie["cast"][:5]])    
        set_tags = set(ref_movie["tag"])
        return (set_genres, set_directors, set_writers, set_cast, set_tags )   
        
    def createDatabase(self):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Kodi', 'Initializing database...')
        
        pDialog.update(10, 'Getting all movies...')
        #jsonkodi.getRequestMoviesThumbs()#
        request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "limits": { "start" : 0, "end": 10000000 }, "properties" : ["genre", "director", "writer", "cast","rating","year", "mpaa", "setid", "imdbnumber", "playcount", "tag", "country", "uniqueid"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        #kodiList = jsonkodi.getDict(jsonkodi.getRequestMovies2(),"movies")
        kodiList = utils.getJSON(self.cachefileDBCreation, request, "movies", 30)
        result = []
        
        for idx1, movie1 in enumerate(kodiList):
            (set_genres, set_directors, set_writers, set_cast, set_tags ) = self.get_sets(movie1)
            if idx1 % 100 == 0:            
                pDialog.update(10 + idx1**2 * 80 // len(kodiList)**2, 'Compare movie: '+movie1["label"])
            for idx2, movie2 in enumerate(kodiList):
                if idx1>idx2 and not utils.compareMovies(movie1, movie2):
                    try:
                        score = self.get_similarity_score(movie1, movie2, set_genres, set_directors, set_writers, set_cast, set_tags)
                    except:
                        score = 0.0
                    
                    if score > 0.5:
                        result.append( (score, utils.reduceMovie(movie1), utils.reduceMovie(movie2) ) )
                        
        pDialog.update(95, 'Reshaping...')
        
        dic = {}
        for (score, movie1, movie2) in result:
            if utils.getTmdbID(movie1) in dic:
                dic[utils.getTmdbID(movie1)]['similar'][utils.getTmdbID(movie2)] = score 
                dic[utils.getTmdbID(movie1)]['similar'] = self.reduceDict(dic[utils.getTmdbID(movie1) ]['similar'], _maxSimilarPerMovie)
            else:
                dic[utils.getTmdbID(movie1)]={'label': movie1['label'], 'similar' : { utils.getTmdbID(movie2)  : score } } 

            if utils.getTmdbID(movie2) in dic:
                dic[utils.getTmdbID(movie2)]['similar'][utils.getTmdbID(movie1)] = score
                dic[utils.getTmdbID(movie2)]['similar'] = self.reduceDict(dic[utils.getTmdbID(movie2) ]['similar'], _maxSimilarPerMovie)
            else:
                dic[utils.getTmdbID(movie2)]={'label': movie2['label'], 'similar' : { utils.getTmdbID(movie1): score } }
                                
        pDialog.close()            
        return dic
    
    
    def saveDatabase(self, lst):
        if self.databaseFile:
            with io.open(self.databaseFile, 'w', encoding='utf8') as json_file:
                data = json.dumps(lst, indent=1, ensure_ascii=False)          
                json_file.write(unicode(data))  
    
    def loadDatabase(self):
        # Read JSON file
        try:
            with io.open(self.databaseFile, 'r', encoding='utf8') as data_file:
                result = json.load(data_file, object_hook=utils.jsonKeys2int)
        except Exception as e:
            utils.log(e)
            result = []
        return result
    
    def getSimilarMovies(self, similarDict, movie):
        try:
            similars = similarDict[utils.getTmdbID(movie) ]
            return similars['similar']
        except Exception as e:
            utils.log(e)     
            return {}
                        
    def printDict(self, dic):
        utils.log("------------BEGIN------------------")
        for i in json.dumps(dic, indent=1).split("\n")[:5]:
            utils.log(i)
        utils.log("-------------END-------------------")
                
    def getRecentlyWatched(self, numberOfRecentlyPlayed):
        request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, "limits": { "start" : 0, "end": '+str(numberOfRecentlyPlayed)+' }, "properties" : ["lastplayed", "playcount", "uniqueid"], "sort": { "order": "descending", "method": "lastplayed" } }, "id": "libMovies"}'        
        return  utils.getJSON(self.cachefileRecent, request, "movies", 7)
    
    def reduceDict(self, dic, maxLen):
        if len<=maxLen:
            return dic
        else:
            sortedList = sorted(dic.items(), key=lambda item: item[1])
            reducedList = sortedList[-maxLen:]
            return dict(reducedList)
           
    def getSimilarMovieListBasedOnRecentMovies(self, numberOfRecentlyPlayed = 30):
        utils.log("Load Similar Movies Database... ")
        similarDict = self.loadDatabase()     
        
        if len(similarDict)==0:
            similarDict = self.createDatabase()
            self.saveDatabase(similarDict)       
        utils.log("Similar Database:")        
        self.printDict(similarDict)
        
        utils.log("Get recent movies... ")
        recentlyWatched = self.getRecentlyWatched(numberOfRecentlyPlayed)
        self.printDict(recentlyWatched)
        
        utils.log("Get similar movies to recent movies... ")
        similar = {}
        for recentMovie in recentlyWatched:
            utils.log("Checking movie: "+repr(recentMovie) )
            thisDict = self.getSimilarMovies(similarDict, recentMovie)
            thisDict = self.reduceDict(thisDict, 10)
            for key in (thisDict):
                thisDict[key] = (thisDict[key], recentMovie['label'])                
            similar.update(thisDict) #add multiple entries to dict
           
        utils.log("Final results of getSimilarMovieListBasedOnRecentMovies:")        
        self.printDict(similar)             
            
        return similar
    

    def hasMatch(self, video, similarIds):
        try:
            (score, similarLabel) = similarIds[utils.getTmdbID(video)]
            video['plot'] = 'Because you watched:'+'\n'+'\n'+similarLabel+"\n"+"\nScore: "+str(score)
            return video
        except:
            return None
                                
        
    def filterSimilarVideos(self, params, videos, similarIds, keyword):
        newvideos = videos
        if 'category' in params:
            for item in params['category'].split(','):
                if keyword in item:
                    newvideos = []
                    for video in videos:
                        match = self.hasMatch(video, similarIds)                
                        if match:
                            video['plot'] = match['plot'] 
                            newvideos.append(video)                
        return newvideos

if __name__ == '__main__':    
    sugg = similarMovieSuggestions('similarMoviesCache.json','similarMoviesCacheRecent.json' 'similarMoviesDB.json')    
    similarUnwatched = sugg.getSimilarMovieListBasedOnRecentMovies(30)
    sugg.printDict(similarUnwatched)
    print("Finished")

