import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import urllib,urllib2
import time
import os
import datetime

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

categories = ['-> List', 'Series', 'Unwatched', 'NoDrama', 'Comedy', 'Action', 'Short', 'Long',  'Old', 'New', 'Good', 'US', 'NoUS', 'Northern', "Horror", "Bad" ]

studio_us = ["Amazon" "Syfy", "FOX" "The CW", "TBS", "SundanceTV", "Showtime", "Playhouse Disney", "Peacock", "FXX", "CBS", "AMC", "ABC (AU)", "ABC (US)", "Comedy Central (US)", "FOX (US)", "HBO", "History", "Netflix", "National Geographic (US)", "FX (US)", "SciFi", "TNT (US)", "Disney Channel", "Disney XD", "USA Network", "Science Channel", "NBC", "Adult Swim"]
studio_br = [ "ITV", "ITV1", "ITV2", "E4", "Channel 4", "BBC", "BBC America", "BBC One", "BBC Three", "BBC Two", "Acorn TV"]
studio_ger = ["TNT Serie" "Maxdome" "VOX", "Das Erste", "MDR", "Hulu", "Arte", "NDR", "Sat.1", "SAT.1", "Tele 5", "WDR", "ZDF", "ZDFneo", "RTL", "RTL Television", "ORF 1", "Radio Bremen", "SWR", "Sky1", "A&E", "BR"]
studio_fr = ["France 2", "Canal+", "TF1"]
studio_misc = ["El Rey Network", "Movistar+", "Rai 1"]
studio_nonorthern = []
studio_nonorthern.extend(studio_us)
studio_nonorthern.extend(studio_br)
studio_nonorthern.extend(studio_ger)
studio_nonorthern.extend(studio_fr)
studio_nonorthern.extend(studio_misc)



def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def list_categories(params):    
    xbmc.log("List category: "+str(params),level=xbmc.LOGWARNING)
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        if (not "category" in params) or (category not in params['category']) or (category == categories[0]): 
            list_item = xbmcgui.ListItem(label=category)#, thumbnailImage=VIDEOS[category][0]['thumb'])
                 
            list_item.setInfo('video', {'title': category, 'genre': category})       
            
            if category == categories[0]:
                newAction = 'listing'
                newCategory = params.get('category','')
            else:           
                newAction = 'category'
                
                if 'category' in params:
                    newCategory = params['category']+','+category
                else:
                    newCategory = category
            
            url = __url__+'?'+'action='+newAction+'&'+'category=' + newCategory
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(__handle__)

def getJSON(url, select):
    html = ""    
    try:    
        html = xbmc.executeJSONRPC(url)
        xbmc.log("List videos: "+html[:200],level=xbmc.LOGWARNING)
        js = json.loads(html) #convert json -> dic        
        return js['result'][select]
    except Exception as e:        
        xbmc.log('Syncplayer: Json Error: '+str(e) +' Url='+str(url) + ' Response' + str(html), level=xbmc.LOGNOTICE)
        return {}


def get_movies(params): 
        
        
    url = ''
    filter = []# '"operator": "contains", "field": "title", "value": "Star Wars"'
    
    xbmc.log("List videos: "+str(params),level=xbmc.LOGWARNING)
    
    if 'Series' in params['category'].split(','):                                                          
        method = 'tvshows'
        properties = '["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "runtime", "imdbnumber", "plot", "studio" ]'    #"tagline",    "trailer",
    else:
        method = 'movies'
        properties = '["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "runtime", "imdbnumber", "plot", "country", "tagline", "trailer", "streamdetails"]' 
    
    for item in params['category'].split(','):
        if 'Series' == item: 
            #method = 'tvshows'
            #do nothing
            pass
        elif item == 'Unwatched':
            filter.append('{"field": "playcount", "operator": "is", "value": "0"}') #ok       
        elif item == 'NoDrama':
           filter.append('{"field": "genre", "operator": "doesnotcontain", "value": "Drama"}') #ok 
        elif item == 'Comedy':
            if method == 'series':            
                filter.append('{"field": "genre", "operator": "contains", "value": "Comedy"}') #ok
            else:
                filter.append('{"field": "genre", "operator": "contains", "value": "Kom"}') #ok
        elif item == 'Action':
           filter.append('{"field": "genre", "operator": "contains", "value": "Action"}') #ok
        elif item == 'Horror':
           filter.append('{"field": "genre", "operator": "contains", "value": "Horror"}') #ok
        elif item == 'Short':
           filter.append('{"field": "time", "operator": "lessthan", "value": "01:15:00"}') #ok
        elif item == 'Long':
           filter.append('{"field": "time", "operator": "greaterthan", "value": "01:45:00"}') #OK
        elif item == 'Old':
           filter.append('{"field": "year", "operator": "lessthan", "value": "1990"}') #ok
        elif item == 'New':
           filter.append('{"field": "year", "operator": "greaterthan", "value": "2010"}') #ok
        elif item == 'Good':
           filter.append('{"field": "rating", "operator": "greaterthan", "value": "7"}') #ok
        elif item == 'Bad':
           filter.append('{"field": "rating", "operator": "lessthan", "value": "5.6"}') #ok
        elif item == 'US':
           filter.append('{"field": "country", "operator": "contains", "value": "United States"}') #ok
        elif item == 'NoUS':
           filter.append('{"field": "country", "operator": "doesnotcontain", "value": "United States"}') #ok
        elif item == 'Northern':
            if method != 'tvshows': 
                filter.append('{"field": "country", "operator": "contains", "value": ["Sweden", "Norway", "Denmark", "Finland", "Iceland"] } ')
            else:
                filter.append('{"field": "studio", "operator": "doesnotcontain", "value": '+ json.dumps(studio_nonorthern)+' } ')
        else: #'Show'
            raise Exception("Wrong category: "+str(item))
        
    if len(filter)==0 :
        filterStr = ''
    elif len(filter)==1 :
        filterStr = '"filter": '+filter[0] + ' , '
    else:    
        filterStr = '"filter": { "and": [' + ",".join(filter) + '] }, '  
        #[ { "field": "genre", "operator": "contains", "value": [ "Film-Noir" ] }, { "field": "tag", "operator": "contains", "value": [ "classic noir", "film noir", "french noir", "brit noir" ] } ] }            # "season", "episode",
        
    request = '{"jsonrpc": "2.0", "params": {"sort": {"order": "ascending", "method": "title"}, '+filterStr+' "properties": '+properties+'}, "method": "VideoLibrary.Get'+method+'", "id": "lib'+method+'"}'
    
    xbmc.log("Request: "+str(request),level=xbmc.LOGWARNING)
                    
    #request = '{"jsonrpc": "2.0", "params": {"sort": {"order": "ascending", "method": "title"}, "filter": {"operator": "contains", "field": "title", "value": "Star Wars"}, "properties": ["title", "art", "file"]}, "method": "VideoLibrary.GetMovies", "id": "libMovies"}'    
    return getJSON(request, method)
    
def getInfoStr(video):
    result = ''
    for k, v in video.items():        
        if 'movieid' != k and 'thumbnail' != k and 'label' != k:
            

            try:
                result = result + str(k)
            except:
                result = result + k.encode('utf-8')
                     
            result = result + ': '

            if isinstance(v, list):
                vlist = v
            else:
                vlist = [v]
            
            for vv in vlist:                 
                try: 
                    if k == "runtime":
                        result = result + time.strftime('%H:%M', time.gmtime(vv))   
                    elif k == "file":
                        result = result + os.path.basename(vv.encode('utf-8'))
                    elif isinstance(vv, float):
                        result = result + str(round(vv,1))
                    else:
                        result = result + str(vv)
                except:
                    result = result + vv.encode('utf-8')
                    
                result = result + ','
            
            
            result = result.rstrip(',') + '\n'   
    return result.rstrip('\n')


def cleanStr(lst):
    result = ''
    
    if isinstance(lst, list):
        vlist = lst
    else:
        vlist = [lst]
    
    for item in vlist:
        try: 
            temp = str(item)
        except:
            temp = item.encode('utf-8')
        
        result = result + temp + ','
        
    return result.rstrip(',')    
        

def list_videos(params):
    # Get the list of videos in the category.
    videos = get_movies(params)#get_videos(category)    
     
    xbmc.log("List videos: "+str(videos),level=xbmc.LOGWARNING)
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        
        xbmc.log("List videos: "+str(video),level=xbmc.LOGWARNING)
        try:
            thumbnailImage=video['thumbnail']
        except:
            thumbnailImage = ''
            
        list_item = xbmcgui.ListItem(label=video['label'], label2=str(video['rating']))
        
               
        list_item.setInfo( type="video", infoLabels={
            "Title": video['label'] , 
            "Year": video['year'],  
            "Genre": cleanStr(video.get('genre','')), 
            "Country": cleanStr(video.get('country', "")),
            'Plot': cleanStr(video.get('plot')), #getInfoStr(video),
            "Tagline": cleanStr(video.get('tagline')),
            'Rating': video['rating'],  
            "Playcount":video['playcount'], 
            "Trailer": video.get('trailer'),            
            "label2": str(round(video['rating'],1)), 
            "mediatype": "movie" 
            } )
        
        list_item.setProperty('fanart_image', thumbnailImage)        
        list_item.setProperty("totaltime", str(video['runtime']))                
        list_item.setProperty("dbid", str(video.get('movieid')))
        list_item.setProperty("imdbnumber", str(video.get('imdbnumber')))    
        list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('IsFolder', 'false')
        
        list_item.setArt( {'thumb': thumbnailImage, 'poster': thumbnailImage, 'banner': thumbnailImage, 'fanart': thumbnailImage, 'icon': thumbnailImage} )                    
        list_item.setThumbnailImage(thumbnailImage)
        list_item.setIconImage(thumbnailImage)                
                
       
        try:        
            list_item.addStreamInfo("video", video['streamdetails']['video'][0] )
        except:
            list_item.addStreamInfo("video", {'duration': video['runtime']} )      
                           
    
                
        url = '{0}?action=play&video={1}'.format(__url__, video.get('file','').encode('utf-8'))
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
      
    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)
    
    
def play_video(path):    
    # Create a playable item with a path to play.
    xbmc.log("Play Item:  "+str(path),level=xbmc.LOGWARNING)
    play_item = xbmcgui.ListItem(path=path['video'])
    #xbmc.log("Play Item:  "+str(play_item)+'-----------------'+str(path),level=xbmc.LOGWARNING) 
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)
    
#def popup(title, s):
#    xbmc.executebuiltin('Notification('+title.replace(",","_")+','+s.replace(",","_")+',5000,'+__icon__+')')    

def router(paramstring):

    xbmcplugin.setContent(__handle__, 'movies')    
        
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_RATING)    
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DURATION )
    xbmc.executebuiltin("Container.SortDirection(%s)" % ("Descending"))

    params = dict(parse_qsl(paramstring))
    
    xbmc.log("Router:  "+str(paramstring),level=xbmc.LOGWARNING)    
    
    if 'action' not in params:
        params['action']='category'
        
    #popup(params['action'], params.get('category','No category'))
    
    xbmcplugin.setPluginCategory(__handle__, params.get('category','No category'))
        
    # Check the parameters passed to the plugin    
    if params['action'] == 'listing':
        # Display the list of videos in a provided category.
        list_videos(params)
    elif params['action'] == 'play':
        # Play a video from a provided URL.
        play_video(params)
    elif params['action'] == 'category':
        # If the plugin is called from Kodi UI without any parameters, display the list of video categories
        list_categories(params)
    else:
        raise Exception('Unknown action')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])