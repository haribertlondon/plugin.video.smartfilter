"""SmartFilter Kodi Addon - Filters and displays videos from Kodi library."""
import sys
from urllib.parse import parse_qsl
from typing import Dict, List, Optional, Any
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

# Constants
LIST_STR = '-> List'
CATEGORY_TRAILER = 'Trailer'
CATEGORY_SHUFFLE = 'Shuffle'
CATEGORY_SERIES = 'Series'
CATEGORY_UNWATCHED = 'Unwatched'
CATEGORY_NODRAMA = 'NoDrama'
CATEGORY_COMEDY = 'Comedy'
CATEGORY_ACTION = 'Action'
CATEGORY_SHORT = 'Short'
CATEGORY_LONG = 'Long'
CATEGORY_OLD = 'Old'
CATEGORY_NEW = 'New'
CATEGORY_GOOD = 'Good'
CATEGORY_US = 'US'
CATEGORY_NOUS = 'NoUS'
CATEGORY_NORTHERN = 'Northern'
CATEGORY_HORROR = 'Horror'
CATEGORY_BAD = 'Bad'
CATEGORY_GERMAN = 'German'
CATEGORY_CRIME = 'Crime'

ACTION_LISTING = 'listing'
ACTION_PLAY = 'play'
ACTION_CATEGORY = 'category'
ACTION_SHOWSERIES = 'showseries'

METHOD_TVSHOWS = 'tvshows'
METHOD_MOVIES = 'movies'

cachefile = os.path.join(__path__, "cachefile.txt")
categories = [LIST_STR, CATEGORY_TRAILER, CATEGORY_SHUFFLE, CATEGORY_SERIES, CATEGORY_UNWATCHED, CATEGORY_NODRAMA, CATEGORY_COMEDY, CATEGORY_ACTION, CATEGORY_SHORT, CATEGORY_LONG, CATEGORY_OLD, CATEGORY_NEW, CATEGORY_GOOD, CATEGORY_US, CATEGORY_NOUS, CATEGORY_NORTHERN, CATEGORY_HORROR, CATEGORY_BAD, CATEGORY_GERMAN, CATEGORY_CRIME]
studio_us = ["Amazon", "Syfy", "FOX", "The CW", "TBS", "SundanceTV", "Showtime", "Playhouse Disney", "Peacock", "FXX", "CBS", "AMC", "ABC (AU)", "ABC (US)", "Comedy Central (US)", "FOX (US)", "HBO", "History", "Netflix", "National Geographic (US)", "FX (US)", "SciFi", "TNT (US)", "Disney Channel", "Disney XD", "USA Network", "Science Channel", "NBC", "Adult Swim"]
studio_br = ["ITV", "ITV1", "ITV2", "E4", "Channel 4", "BBC", "BBC America", "BBC One", "BBC Three", "BBC Two", "Acorn TV"]
studio_ger = ["TNT Serie", "Maxdome", "VOX", "Das Erste", "MDR", "Hulu", "Arte", "NDR", "Sat.1", "SAT.1", "Tele 5", "WDR", "ZDF", "ZDFneo", "RTL", "RTL Television", "ORF 1", "Radio Bremen", "SWR", "Sky1", "A&E", "BR"]
studio_fr = ["France 2", "Canal+", "TF1"]
studio_misc = ["El Rey Network", "Movistar+", "Rai 1"]
studio_nonorthern = studio_us + studio_br + studio_ger + studio_fr + studio_misc


def list_categories(params: Dict[str, str]) -> None:
    utils.log(f"List category: {params}")
    listing = []
    
    for category in categories:
        if ("category" not in params) or (category not in params['category']) or (category == categories[0]):
            list_item = xbmcgui.ListItem(label=category)
            list_item.setInfo('video', {'title': category, 'genre': category})

            if category == LIST_STR:
                new_action = ACTION_LISTING
                new_category = params.get('category', '')
            else:
                new_action = ACTION_CATEGORY
                if 'category' in params:
                    new_category = f"{params['category']},{category}"
                else:
                    new_category = category

            url = f"{__url__}?action={new_action}&category={new_category}"
            is_folder = True
            listing.append((url, list_item, is_folder))
    
    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def key_in_params(params: Dict[str, str], key: str) -> bool:
    if 'category' in params and key in params['category'].split(','):
        return True
    return False


def is_series(params: Dict[str, str]) -> bool:
    return key_in_params(params, CATEGORY_SERIES)

def is_shuffle(params: Dict[str, str]) -> bool:
    return key_in_params(params, CATEGORY_SHUFFLE)

def is_trailer(params: Dict[str, str]) -> bool:
    return key_in_params(params, CATEGORY_TRAILER)

def build_filter_for_category(item: str, method: str) -> Optional[Dict[str, Any]]:
    if item == CATEGORY_SERIES:
        return None
    elif item == CATEGORY_UNWATCHED:
        return {"field": "playcount", "operator": "is", "value": "0"}
    elif item == CATEGORY_NODRAMA:
        return {"field": "genre", "operator": "doesnotcontain", "value": "Drama"}
    elif item == CATEGORY_COMEDY:
        genre_value = "Com" if method == METHOD_TVSHOWS else "Kom"
        return {"field": "genre", "operator": "contains", "value": genre_value}
    elif item == CATEGORY_ACTION:
        return {"field": "genre", "operator": "contains", "value": "Action"}
    elif item == CATEGORY_CRIME:
        genre_value = "Crime" if method == METHOD_TVSHOWS else "Krimi"
        return {"field": "genre", "operator": "contains", "value": genre_value}
    elif item == CATEGORY_HORROR:
        return {"field": "genre", "operator": "contains", "value": "Horror"}
    elif item == CATEGORY_SHORT:
        if method == METHOD_TVSHOWS:
            return {"field": "numepisodes", "operator": "lessthan", "value": "20"}
        else:
            return {"field": "time", "operator": "lessthan", "value": "01:15:00"}
    elif item == CATEGORY_LONG:
        if method == METHOD_TVSHOWS:
            return {"field": "numepisodes", "operator": "greaterthan", "value": "20"}
        else:
            return {"field": "time", "operator": "greaterthan", "value": "01:45:00"}
    elif item == CATEGORY_OLD:
        return {"field": "year", "operator": "lessthan", "value": "1990"}
    elif item == CATEGORY_NEW:
        return {"field": "year", "operator": "greaterthan", "value": "2010"}
    elif item == CATEGORY_GOOD:
        return {"field": "rating", "operator": "greaterthan", "value": "7"}
    elif item == CATEGORY_BAD:
        return {"field": "rating", "operator": "lessthan", "value": "5.6"}
    elif item == CATEGORY_US:
        if method == METHOD_TVSHOWS:
            return {"field": "studio", "operator": "contains", "value": studio_us}
        else:
            return {"field": "country", "operator": "contains", "value": "United States"}
    elif item == CATEGORY_NOUS:
        if method == METHOD_TVSHOWS:
            return {"field": "studio", "operator": "doesnotcontain", "value": studio_us}
        else:
            return {"field": "country", "operator": "doesnotcontain", "value": "United States"}
    elif item == CATEGORY_GERMAN:
        if method == METHOD_TVSHOWS:
            return {"field": "studio", "operator": "doesnotcontain", "value": studio_ger}
        else:
            return {"field": "country", "operator": "contains", "value": "Germany"}
    elif item == CATEGORY_NORTHERN:
        if method == METHOD_TVSHOWS:
            return {"field": "studio", "operator": "doesnotcontain", "value": studio_nonorthern}
        else:
            return {"field": "country", "operator": "contains", "value": ["Sweden", "Norway", "Denmark", "Finland", "Iceland"]}
    else:
        raise ValueError(f"Unknown category: {item}")


def build_jsonrpc_request(method: str, filters: List[Dict[str, Any]], properties: List[str]) -> str:
    params = {"sort": {"order": "ascending", "method": "title"}, "properties": properties}
    if len(filters) == 1:
        params["filter"] = filters[0]
    elif len(filters) > 1:
        params["filter"] = {"and": filters}
    request = {"jsonrpc": "2.0", "params": params, "method": f"VideoLibrary.Get{method}", "id": f"lib{method}"}
    return json.dumps(request)


def get_movies(params: Dict[str, str]) -> List[Dict[str, Any]]:
    filters = []
    utils.log(f"List get_movies params: {params}")
    if key_in_params(params, CATEGORY_SERIES):
        method = METHOD_TVSHOWS
        properties = ["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "dateadded", "runtime", "imdbnumber", "uniqueid", "studio"]
    else:
        method = METHOD_MOVIES
        properties = ["title", "thumbnail", "file", "genre", "rating", "year", "playcount", "lastplayed", "dateadded", "runtime", "imdbnumber", "uniqueid", "country", "tagline", "trailer", "streamdetails"]

    if 'category' in params:
        for item in params['category'].split(','):
            filter_obj = build_filter_for_category(item, method)
            if filter_obj is not None:
                filters.append(filter_obj)

    request = build_jsonrpc_request(method, filters, properties)
    utils.log(f"Request: {request}")
    
    lst = utils.getJSON(cachefile, request, method)
    utils.log(f"Found movies: #{len(lst)}")
    
    return lst

def clean_str(lst: Any) -> str:
    if isinstance(lst, list):
        vlist = lst
    else:
        vlist = [lst]
    
    result_parts = []
    for item in vlist:
        try:
            temp = str(item)
        except (UnicodeEncodeError, AttributeError) as e:
            utils.log(f"Error encoding item {item}: {e}")
            temp = repr(item)
        
        result_parts.append(temp)
    
    return ','.join(result_parts)

def list_videos(params: Dict[str, str]) -> None:
    if not is_shuffle(params):
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DURATION)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATEADDED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_PLAYCOUNT)
        xbmc.executebuiltin("Container.SortDirection(Descending)")
    else:
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_NONE)

    videos = get_movies(params)

    if is_shuffle(params):
        random.shuffle(videos)

    utils.log(f"Listing videos {len(videos)}")
    listing = []
    
    for video in videos:
        try:
            thumbnail_image = video['thumbnail']
        except (KeyError, TypeError):
            thumbnail_image = ''

        list_item = xbmcgui.ListItem(label=video['label'], label2=str(video['rating']))

        plot_text = clean_str(video.get('plot')) if video.get('plot') else "-Deactivated-"
        tagline_text = f"{clean_str(video.get('genre', '')).replace(',', ', ')}\n\n{clean_str(video.get('tagline'))}"
        list_item.setInfo(type="video", infoLabels={"title": f"{video['label']} ({clean_str(video['year'])}) ", "year": video['year'], "genre": clean_str(video.get('genre', '')), "country": clean_str(video.get('country', "")), 'plot': plot_text, "tagline": tagline_text, 'rating': video['rating'], "playcount": video['playcount'], "trailer": video.get('trailer'), "label2": str(round(video['rating'], 1)), "dateadded": video.get('dateadded', ''), "mediatype": "tvshow" if is_series(params) else "movie"})

        unique_ids = video.get('uniqueid', {})
        if unique_ids:
            default_id = list(unique_ids.keys())[0]
        else:
            default_id = "imdb"
        
        list_item.setUniqueIDs(unique_ids, default_id)
        list_item.setProperty('fanart_image', thumbnail_image)
        list_item.setProperty("totaltime", str(video['runtime']))
        list_item.setProperty("dbid", str(video.get('movieid')))
        list_item.setProperty("imdbnumber", str(video.get('imdbnumber')))

        list_item.setArt({'thumb': thumbnail_image, 'poster': thumbnail_image, 'banner': thumbnail_image, 'fanart': thumbnail_image, 'icon': thumbnail_image})

        try:
            list_item.addStreamInfo("video", video['streamdetails']['video'][0])
        except (KeyError, IndexError, TypeError):
            list_item.addStreamInfo("video", {'duration': video['runtime']})

        if is_series(params):
            url = f"{__url__}?action={ACTION_SHOWSERIES}&tvshowid={video.get('tvshowid', '')}"
            list_item.setProperty('IsPlayable', 'false')
            list_item.setProperty('IsFolder', 'true')
        else:
            if is_trailer(params):
                url = f"{__url__}?action={ACTION_PLAY}&video={video.get('trailer', '')}"
            else:
                url = f"{__url__}?action={ACTION_PLAY}&video={video.get('file', '')}"
            list_item.setProperty('IsPlayable', 'true')
            list_item.setProperty('IsFolder', 'false')
        
        is_folder = False
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)

def show_series(path: Dict[str, str]) -> None:
    utils.log(f"Show series: {path}")
    try:
        tvshowid = path['tvshowid']
        utils.log(f"--------------------------- Opening series: {tvshowid}")
        url = json.dumps({"jsonrpc": "2.0", "method": "GUI.ActivateWindow", "id": tvshowid, "params": {"window": "videos", "parameters": ["TvShowTitles"]}})
        html = xbmc.executeJSONRPC(url)
        utils.log(html)
    except (KeyError, TypeError) as e:
        utils.log(f"Error showing series: {e}")


def play_video(path: Dict[str, str]) -> None:
    utils.log(f"Play Item: {path}")
    try:
        filename = path['video']
        utils.log(f"Clean Item: {filename}<>{repr(filename)}")
        
        play_item = xbmcgui.ListItem(path=filename)
        try:
            xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)
        except (RuntimeError, AttributeError) as e:
            utils.log(f"Error playing video with setResolvedUrl: {e}")
            try:
                xbmc.Player().play(filename)
            except Exception as e2:
                utils.log(f"Error playing video with Player().play: {e2}")
    except (KeyError, TypeError) as e:
        utils.log(f"Error accessing video path: {e}")


def router(paramstring: str) -> None:
    utils.log(f"Started smart filter: {__path__}")
    xbmcplugin.setContent(__handle__, 'movies')

    params = dict(parse_qsl(paramstring))
    utils.log(f"Router: {paramstring}")

    if 'action' not in params:
        params['action'] = ACTION_CATEGORY

    xbmcplugin.setPluginCategory(__handle__, params.get('category', 'No category'))

    action = params['action']
    if action == ACTION_LISTING:
        list_videos(params)
    elif action == ACTION_PLAY:
        play_video(params)
    elif action == ACTION_CATEGORY:
        list_categories(params)
    elif action == ACTION_SHOWSERIES:
        show_series(params)
    else:
        raise ValueError(f'Unknown action: {action}')

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])