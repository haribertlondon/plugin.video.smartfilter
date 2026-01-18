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

# Filter configuration: category -> (field, operator, value_getter)
# value_getter can be: string, callable(method), or dict with method keys
FILTER_CONFIG = {
    CATEGORY_UNWATCHED: ("playcount", "is", "0"),
    CATEGORY_NODRAMA: ("genre", "doesnotcontain", "Drama"),
    CATEGORY_COMEDY: ("genre", "contains", lambda m: "Com" if m == METHOD_TVSHOWS else "Kom"),
    CATEGORY_ACTION: ("genre", "contains", "Action"),
    CATEGORY_CRIME: ("genre", "contains", lambda m: "Crime" if m == METHOD_TVSHOWS else "Krimi"),
    CATEGORY_HORROR: ("genre", "contains", "Horror"),
    CATEGORY_SHORT: (lambda m: "numepisodes" if m == METHOD_TVSHOWS else "time", "lessthan", lambda m: "20" if m == METHOD_TVSHOWS else "01:15:00"),
    CATEGORY_LONG: (lambda m: "numepisodes" if m == METHOD_TVSHOWS else "time", "greaterthan", lambda m: "20" if m == METHOD_TVSHOWS else "01:45:00"),
    CATEGORY_OLD: ("year", "lessthan", "1990"),
    CATEGORY_NEW: ("year", "greaterthan", "2010"),
    CATEGORY_GOOD: ("rating", "greaterthan", "7"),
    CATEGORY_BAD: ("rating", "lessthan", "5.6"),
    CATEGORY_US: (lambda m: "studio" if m == METHOD_TVSHOWS else "country", "contains", lambda m: studio_us if m == METHOD_TVSHOWS else "United States"),
    CATEGORY_NOUS: (lambda m: "studio" if m == METHOD_TVSHOWS else "country", "doesnotcontain", lambda m: studio_us if m == METHOD_TVSHOWS else "United States"),
    CATEGORY_GERMAN: (lambda m: "studio" if m == METHOD_TVSHOWS else "country", lambda m: "doesnotcontain" if m == METHOD_TVSHOWS else "contains", lambda m: studio_ger if m == METHOD_TVSHOWS else "Germany"),
    CATEGORY_NORTHERN: (lambda m: "studio" if m == METHOD_TVSHOWS else "country", lambda m: "doesnotcontain" if m == METHOD_TVSHOWS else "contains", lambda m: studio_nonorthern if m == METHOD_TVSHOWS else ["Sweden", "Norway", "Denmark", "Finland", "Iceland"]),
}

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
    if item not in FILTER_CONFIG:
        raise ValueError(f"Unknown category: {item}")
    config = FILTER_CONFIG[item]
    field = config[0](method) if callable(config[0]) else config[0]
    operator = config[1](method) if callable(config[1]) else config[1]
    value = config[2](method) if callable(config[2]) else config[2]
    return {"field": field, "operator": operator, "value": value}

def build_external_filters(params: Dict[str, str], method: str) -> List[Dict[str, Any]]:
    filters = []
    
    # Genre include list
    if 'genre' in params or 'genres' in params:
        genre_param = params.get('genre') or params.get('genres', '')
        if genre_param:
            genres = [g.strip() for g in genre_param.split(',') if g.strip()]
            if genres:
                filters.append({"field": "genre", "operator": "contains", "value": genres})
    
    # Genre exclude list
    if 'genre_exclude' in params or 'genres_exclude' in params:
        genre_exclude_param = params.get('genre_exclude') or params.get('genres_exclude', '')
        if genre_exclude_param:
            genres_exclude = [g.strip() for g in genre_exclude_param.split(',') if g.strip()]
            for genre in genres_exclude:
                filters.append({"field": "genre", "operator": "doesnotcontain", "value": genre})
    
    # Year range
    if 'year_min' in params:
        try:
            year_min = int(params['year_min'])
            filters.append({"field": "year", "operator": "greaterthan", "value": str(year_min - 1)})
        except ValueError:
            utils.log(f"Invalid year_min value: {params['year_min']}")
    
    if 'year_max' in params:
        try:
            year_max = int(params['year_max'])
            filters.append({"field": "year", "operator": "lessthan", "value": str(year_max + 1)})
        except ValueError:
            utils.log(f"Invalid year_max value: {params['year_max']}")
    
    # Rating range
    if 'rating_min' in params:
        try:
            rating_min = float(params['rating_min'])
            filters.append({"field": "rating", "operator": "greaterthan", "value": str(rating_min)})
        except ValueError:
            utils.log(f"Invalid rating_min value: {params['rating_min']}")
    
    if 'rating_max' in params:
        try:
            rating_max = float(params['rating_max'])
            filters.append({"field": "rating", "operator": "lessthan", "value": str(rating_max)})
        except ValueError:
            utils.log(f"Invalid rating_max value: {params['rating_max']}")
    
    # Duration range
    if 'duration_min' in params:
        try:
            duration_min = params['duration_min']
            if method == METHOD_TVSHOWS:
                # For TV shows: numepisodes (number)
                filters.append({"field": "numepisodes", "operator": "greaterthan", "value": str(int(duration_min))})
            else:
                # For movies: time (HH:MM:SS format)
                if ':' not in duration_min:
                    # Assume seconds, convert to HH:MM:SS
                    duration_min_sec = int(duration_min)
                    duration_min = time.strftime('%H:%M:%S', time.gmtime(duration_min_sec))
                filters.append({"field": "time", "operator": "greaterthan", "value": duration_min})
        except (ValueError, AttributeError) as e:
            utils.log(f"Invalid duration_min value: {params['duration_min']}, error: {e}")
    
    if 'duration_max' in params:
        try:
            duration_max = params['duration_max']
            if method == METHOD_TVSHOWS:
                # For TV shows: numepisodes (number)
                filters.append({"field": "numepisodes", "operator": "lessthan", "value": str(int(duration_max))})
            else:
                # For movies: time (HH:MM:SS format)
                if ':' not in duration_max:
                    # Assume seconds, convert to HH:MM:SS
                    duration_max_sec = int(duration_max)
                    duration_max = time.strftime('%H:%M:%S', time.gmtime(duration_max_sec))
                filters.append({"field": "time", "operator": "lessthan", "value": duration_max})
        except (ValueError, AttributeError) as e:
            utils.log(f"Invalid duration_max value: {params['duration_max']}, error: {e}")
    
    return filters


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

    # Build filters from category parameters
    if 'category' in params:
        for item in params['category'].split(','):
            filter_obj = build_filter_for_category(item, method)
            if filter_obj is not None:
                filters.append(filter_obj)
    
    # Build filters from external parameters (genre, year, duration, rating)
    external_filters = build_external_filters(params, method)
    filters.extend(external_filters)

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

    # Movies from 2010-2020 with Action genre, rating 7+, excluding Drama
    #?action=listing&genre=Action&year_min=2010&year_max=2020&rating_min=7.0&genre_exclude=Drama

    # TV shows with 10-30 episodes, Comedy genre
    #?action=listing&category=Series&genres=Comedy&duration_min=10&duration_max=30

    # Combine with existing categories
    #?action=listing&category=Unwatched,Good&year_min=2015&rating_min=8.0

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