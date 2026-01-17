import sys
from urllib.parse import parse_qsl
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import random
import time
import os
import utils

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__path__ = __addon__.getAddonInfo('path')

_listStr='-> List'

cachefile = __path__ + "/cachefile.txt"
categories = [_listStr, 'Trailer', "Shuffle", 'Series', 'Unwatched', 'NoDrama', 'Comedy', 'Action', 'Short', 'Long',  'Old', 'New', 'Good', 'US', 'NoUS', 'Northern', "Horror", "Bad", "German", "Crime"]
studio_us = ["Amazon" "Syfy", "FOX" "The CW", "TBS", "SundanceTV", "Showtime", "Playhouse Disney", "Peacock", "FXX", "CBS", "AMC", "ABC (AU)", "ABC (US)", "Comedy Central (US)", "FOX (US)", "HBO", "History", "Netflix", "National Geographic (US)", "FX (US)", "SciFi", "TNT (US)", "Disney Channel", "Disney XD", "USA Network", "Science Channel", "NBC", "Adult Swim"]
studio_br = [ "ITV", "ITV1", "ITV2", "E4", "Channel 4", "BBC", "BBC America", "BBC One", "BBC Three", "BBC Two", "Acorn TV"]
studio_ger = ["TNT Serie" "Maxdome" "VOX", "Das Erste", "MDR", "Hulu", "Arte", "NDR", "Sat.1", "SAT.1", "Tele 5", "WDR", "ZDF", "ZDFneo", "RTL", "RTL Television", "ORF 1", "Radio Bremen", "SWR", "Sky1", "A&E", "BR"]
studio_fr = ["France 2", "Canal+", "TF1"]
studio_misc = ["El Rey Network", "Movistar+", "Rai 1"]
studio_nonorthern = studio_us  + studio_br + studio_ger + studio_fr + studio_misc

def list_categories(params):
    utils.log("List category: "+str(params))
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        if ("category" not in params) or (category not in params['category'] ) or (category == categories[0]):

            list_item = xbmcgui.ListItem(label=category)# + ": #" + str(len(lst)))#

            list_item.setInfo('video', {'title': category, 'genre': category})

            if category == _listStr:
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


def keyInParams(params, key):
    if ('category' in params and key in params['category'].split(',')):
        return True
    else:
        return False

def isSeries(params):
    return keyInParams(params, 'Series')

def isShuffle(params):
    return keyInParams(params, 'Shuffle')

def isTrailer(params):
    return keyInParams(params, 'Trailer')

def get_movies(params):
    filter = []
    utils.log("List get_movies params: "+str(params))

    if keyInParams(params, 'Series'):
        method = 'tvshows'
        properties = '["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "dateadded", "runtime", "imdbnumber", "uniqueid",  "studio" ]'    #"tagline",    "trailer",
    else:
        method = 'movies'
        properties = '["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "dateadded", "runtime", "imdbnumber", "uniqueid",  "country", "tagline", "trailer", "streamdetails"]'

    if 'category' in params:
        for item in params['category'].split(','):
            if 'Series' == item:
                #do nothing
                pass
            elif item == 'Unwatched':
                filter.append('{"field": "playcount", "operator": "is", "value": "0"}') 
            elif item == 'NoDrama':
                filter.append('{"field": "genre", "operator": "doesnotcontain", "value": "Drama"}') 
            elif item == 'Comedy':
                if method == 'tvshows':
                    filter.append('{"field": "genre", "operator": "contains", "value": "Com"}') 
                else:
                    filter.append('{"field": "genre", "operator": "contains", "value": "Kom"}') 
            elif item == 'Action':
                filter.append('{"field": "genre", "operator": "contains", "value": "Action"}') 
            elif item == 'Crime':
                if method == 'tvshows':
                    filter.append('{"field": "genre", "operator": "contains", "value": "Crime"}')
                else:
                    filter.append('{"field": "genre", "operator": "contains", "value": "Krimi"}')
            elif item == 'Horror':
                filter.append('{"field": "genre", "operator": "contains", "value": "Horror"}') 
            elif item == 'Short':
                if method == 'tvshows':
                    filter.append('{"field": "numepisodes", "operator": "lessthan", "value": "20"}')
                else:
                    filter.append('{"field": "time", "operator": "lessthan", "value": "01:15:00"}') 
            elif item == 'Long':
                if method == 'tvshows':
                    filter.append('{"field": "numepisodes", "operator": "greaterthan", "value": "20"}')
                else:
                    filter.append('{"field": "time", "operator": "greaterthan", "value": "01:45:00"}') 
            elif item == 'Old':
                filter.append('{"field": "year", "operator": "lessthan", "value": "1990"}') 
            elif item == 'New':
                filter.append('{"field": "year", "operator": "greaterthan", "value": "2010"}') 
            elif item == 'Good':
                filter.append('{"field": "rating", "operator": "greaterthan", "value": "7"}') 
            elif item == 'Bad':
                filter.append('{"field": "rating", "operator": "lessthan", "value": "5.6"}') 
            elif item == 'US':
                if method == 'tvshows':
                    filter.append('{"field": "studio", "operator": "contains", "value": '+ json.dumps(studio_us)+' } ')  
                else:
                    filter.append('{"field": "country", "operator": "contains", "value": "United States"}') 
            elif item == 'NoUS':
                if method == 'tvshows':
                    filter.append('{"field": "studio", "operator": "doesnotcontain", "value": '+ json.dumps(studio_us)+' } ') 
                else:
                    filter.append('{"field": "country", "operator": "doesnotcontain", "value": "United States"}') 
            elif item == "German":
                if method == 'tvshows':
                    filter.append('{"field": "studio", "operator": "doesnotcontain", "value": '+ json.dumps(studio_ger)+' } ')
                else:
                    filter.append('{"field": "country", "operator": "contains", "value": "Germany" } ')
            elif item == 'Northern':
                if method == 'tvshows':
                    filter.append('{"field": "studio", "operator": "doesnotcontain", "value": '+ json.dumps(studio_nonorthern)+' } ') 
                else:
                    filter.append('{"field": "country", "operator": "contains", "value": ["Sweden", "Norway", "Denmark", "Finland", "Iceland"] } ')             
            else: #'Show'
                raise Exception("Unknown category: "+str(item))

    if len(filter)==0 :
        filterStr = ''
    elif len(filter)==1 :
        filterStr = '"filter": '+filter[0] + ' , '
    else:
        filterStr = '"filter": { "and": [' + ",".join(filter) + '] }, '
        #[ { "field": "genre", "operator": "contains", "value": [ "Film-Noir" ] }, { "field": "tag", "operator": "contains", "value": [ "classic noir", "film noir", "french noir", "brit noir" ] } ] }            # "season", "episode",

    request = '{"jsonrpc": "2.0", "params": {"sort": {"order": "ascending", "method": "title"}, '+filterStr+' "properties": '+properties+'}, "method": "VideoLibrary.Get'+method+'", "id": "lib'+method+'"}'

    utils.log("Request: "+str(request))
    
    lst = utils.getJSON(cachefile, request, method)

    utils.log("Found movies: #"+str(len(lst)))    

    return lst

def getInfoStr(video):
    result = ''
    for k, v in list(video.items()):
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

    if not isShuffle(params):
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DURATION )
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATEADDED )
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_GENRE )
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_PLAYCOUNT )
    else:
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_NONE)

    xbmc.executebuiltin("Container.SortDirection(%s)" % ("Descending"))


    # Get the list of videos in the category.
    videos = get_movies(params)

    if isShuffle(params):
        random.shuffle(videos)

    utils.log("Listing videos "+str(len(videos)))
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:

        try:
            thumbnailImage=video['thumbnail']
        except:
            thumbnailImage = ''

        list_item = xbmcgui.ListItem(label=video['label'], label2=str(video['rating']))

        list_item.setInfo( type="video", infoLabels={
            "title": video['label'] + " ("+cleanStr(video['year'])+") " ,
            "year": video['year'],
            "genre": cleanStr(video.get('genre','')),
            "country": cleanStr(video.get('country', "")),
            'plot': cleanStr(video.get('plot')) if video.get('plot') else "-Deactivated-" , #, #getInfoStr(video),
            "tagline": cleanStr(video.get('genre','')).replace(",",", ") + "\n\n" + cleanStr(video.get('tagline')),
            'rating': video['rating'],
            "playcount":video['playcount'],
            "trailer": video.get('trailer'),
            "label2": str(round(video['rating'],1)),
            "dateadded": video.get('dateadded',''),
            "mediatype": "tvshow" if isSeries(params) else "movie"
            } )

        try:
            defaultId = list(video.get('uniqueid',{}).keys())[0]
        except:
            defaultId = "imdb"
        list_item.setUniqueIDs(video.get('uniqueid',{}),  defaultId)
        list_item.setProperty('fanart_image', thumbnailImage)
        list_item.setProperty("totaltime", str(video['runtime']))
        list_item.setProperty("dbid", str(video.get('movieid')))
        list_item.setProperty("imdbnumber", str(video.get('imdbnumber')))


        list_item.setArt( {'thumb': thumbnailImage, 'poster': thumbnailImage, 'banner': thumbnailImage, 'fanart': thumbnailImage, 'icon': thumbnailImage} )

        try:
            list_item.addStreamInfo("video", video['streamdetails']['video'][0] )
        except:
            list_item.addStreamInfo("video", {'duration': video['runtime']} )

        if isSeries(params):
            url = '{0}?action=showseries&tvshowid={1}'.format(__url__, video.get('tvshowid',''))
            list_item.setProperty('IsPlayable', 'false')
            list_item.setProperty('IsFolder', 'true')
        else:
            if isTrailer(params):
                url = '{0}?action=play&video={1}'.format(__url__, video.get('trailer',''))
            else:
                url = '{0}?action=play&video={1}'.format(__url__, video.get('file',''))
            list_item.setProperty('IsPlayable', 'true')
            list_item.setProperty('IsFolder', 'false')
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)

def show_series(path):
    utils.log("Show series:  "+str(path))
    tvshowid = path['tvshowid']
    utils.log("--------------------------- Opening series:  "+str(tvshowid))
    url = json.dumps({"jsonrpc":"2.0","method":"GUI.ActivateWindow","id":tvshowid,"params":{"window":"videos","parameters":["TvShowTitles"]}})
    html = xbmc.executeJSONRPC(url)
    utils.log(html)


def play_video(path):
    # Create a playable item with a path to play.
    utils.log("Play Item:  "+str(path))
    filename = path['video']
    utils.log("Clean Item:  "+str(filename)+"<>"+repr(filename))


    play_item = xbmcgui.ListItem(path=filename)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


def router(paramstring):
    utils.log("Started smart filter:  "+str(__path__))
    xbmcplugin.setContent(__handle__, 'movies')

    params = dict(parse_qsl(paramstring))

    utils.log("Router:  "+str(paramstring))

    if 'action' not in params:
        params['action']='category'

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
    elif params['action'] == 'showseries':
        show_series(params)    
    else:
        raise Exception('Unknown action')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])