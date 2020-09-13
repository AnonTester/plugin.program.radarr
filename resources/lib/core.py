# -*- coding: utf-8 -*-
import sys
import requests
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import time
import threading
import json as simplejson

from resources.lib.radarr_api import RadarrAPI
from resources.lib.listing import add_entries, parameters_string_to_dict
from resources.lib._json import write_json, read_json, get_appended_path,\
     dir_db, dir_movies

addonID = "plugin.program.radarr"
addon = xbmcaddon.Addon(id=addonID)
fanart = ''
pluginhandle = int(sys.argv[1])
xbmc.log("SYSARGV " + str(sys.argv[2]))

loglevel = 1
log_msg = addonID + ' - '
TRANSLATE = addon.getLocalizedString

base_url = addon.getSetting('base-url')
api_key = addon.getSetting('api-key')
addonicon = addon.getAddonInfo('path') + '/icon.png'
addonfanart = addon.getAddonInfo('path') + '/fanart.jpg'
xbmc.log("ICON " + str(addonicon))


vw_miss = False
if addon.getSetting('view-miss') == 'true': vw_miss = True

# Retreive preferred quality from settings
if addon.getSetting('preferred_quality') == 'Choose On Search': quality = 'choose'
if addon.getSetting('preferred_quality') == 'Any': quality = 'any'
if addon.getSetting('preferred_quality') == 'SD': quality = 'sd'
if addon.getSetting('preferred_quality') == 'HD-720p': quality = '720'
if addon.getSetting('preferred_quality') == 'HD-1080p': quality = '1080'
if addon.getSetting('preferred_quality') == 'Ultra-HD': quality = 'ultra'
if addon.getSetting('preferred_quality') == 'HD-720p/1080p': quality = '7201080'

if not base_url.endswith('/'):
    base_url += '/'
host_url = base_url + 'api'

snr = RadarrAPI(host_url, api_key)


def root():
    mall_movies = {'name': TRANSLATE(30005), 'mode': 'getAllMovies', 'type': 'dir', 'images': {'thumb': addonicon, 'fanart': addonfanart}}
    madd_movie = {'name': TRANSLATE(30009), 'mode': 'addMovie', 'type': 'dir', 'images': {'thumb': addonicon, 'fanart': addonfanart}}
    msearch_missing = {'name': TRANSLATE(30010), 'mode': 'searchMissing', 'type': 'dir', 'images': {'thumb': addonicon, 'fanart': addonfanart}}
    mget_queue = {'name': TRANSLATE(30011), 'mode': 'getQueue', 'type': 'dir', 'images': {'thumb': addonicon, 'fanart': addonfanart}}
    main = [madd_movie, mall_movies, msearch_missing, mget_queue]
    add_entries(main)
    xbmcplugin.endOfDirectory(pluginhandle)


def add_movie(term=None):
    dialog = xbmcgui.Dialog()
    term = dialog.input('Add Movie', type=xbmcgui.INPUT_ALPHANUM)
    # if user cancels, return
    if not term:
        return -1
    # movie lookup
    shows = []
    monitored = ''
    data = snr.lookup_movie(term)
    xbmc.log( "DATA: " + str(data))
    for show in data:
        xbmc.log( "MOVIE : " + str(data))
        year = show['year']
        shows.append(show['title'] + " (" + str(year) + ")")
    if not shows:
        # NOTHING FOUND NOTIFICATION
        dialog.notification('Radarr', 'No match was found for the movie "%s"' % term, addonicon, 5000)
        return -1
    # open dialog for choosing movie
    dialog = xbmcgui.Dialog()
    ret = dialog.select(TRANSLATE(30210), shows)
    if ret == -1:
        return -1
    xbmc.log('RET', level=0)

    # open dialog for choosing preferred quality if not specified
    if quality == 'choose':
        quality_profile_id = list_quality_profiles()
        if quality_profile_id == -1:
            return -1
    # set preferred quality if specified
    elif quality == 'any':
        quality_profile_id = 1
    elif quality == 'sd':
        quality_profile_id = 2
    elif quality == '720':
        quality_profile_id = 3
    elif quality == '1080':
        quality_profile_id = 4
    elif quality == 'ultra':
        quality_profile_id = 5
    elif quality == '7201080':
        quality_profile_id = 6

    tmdbId = data[ret]['tmdbId']
    title = data[ret]['title']
    year = data[ret]['year']
    titleSlug = data[ret]['titleSlug']
    images = data[ret]['images']
    data = {
        'title': title,
        'year': year,
        'qualityProfileId': quality_profile_id,
        'titleSlug': titleSlug,
        'tmdbId': tmdbId,
        'images': images,
        'rootFolderPath': snr.get_root_folder()[0]['path'],
        # 'titleSlug': '',
        # 'seasons': [],
        'addOptions': {
             'ignoreEpisodesWithFile': 'false',
             'ignoreEpisodesWithoutFiles': 'false',
             'searchForMovie': 'true'
        }
    }
    xbmc.log("DATASENT " + str(data))
    snr.add_movie(data)
    dialog.notification('Radarr', 'Added to watchlist: "%s"' % title, addonicon, 5000)


def search_missing():
    data = {
        'name': 'missingMoviesSearch',
        'filterKey': 'monitored',
        'filterValue': 'true'
    }
    snr.search_missing(data)

def search_individual(movieid):
    xbmc.log("SearchIndividual " + str(movieid), level=2)
    data = {
        'name': 'MoviesSearch',
        'movieIDs': [movieid]
    }
    snr.search_individual(data)

def list_quality_profiles():
    profiles = []
    data = snr.get_quality_profiles()
    for profile in data:
        profile_id = profile['id']
        profile_name = profile['name']
        profiles.append({'name': profile_name, 'id': profile_id})
    profiles_key_list = []
    for profile in profiles:
        profiles_key_list.append(profile['name'])
    dialog = xbmcgui.Dialog()
    ret = dialog.select(TRANSLATE(30211), profiles_key_list)
    if ret == -1:
        return -1
    id = profiles[ret]['id']
    return id


def list_movies(data):
    shows = []
    qdata = snr.get_queue()
    xbmc.log( "LISTT: QDATA" + str(qdata))
    qshows = []
    qnames = []
    for qshow in qdata:
        xbmc.log( "LISTT: " + str(qnames))
        name = qshow['movie']['title']
        qnames.append((name))
        thumb = qshow['movie']['images'][0]['url']
        fanart = qshow['movie']['images'][1]['url']
        totalsize = qshow['size'] * 1e-9
        perc = 100 - (100 * float(qshow['sizeleft'])/float(qshow['size']))
        name += '   [COLOR FF00FF00]Downloading %s%%[/COLOR] ' % round(perc, 1)
        name += ' [COLOR FF00FF00]of  %sGB[/COLOR] ' % round(totalsize, 2)
        show_id = qshow['movie']['id']
        seasons = 'na'
        dir_show = get_appended_path(dir_movies, str(show_id))
        file = 'seasons.json'
        file_path = get_appended_path(dir_show, file)
        write_json(file_path, seasons)
        shows.append({'name': name, 'url': str(show_id), 'mode': 'getMovie', 'type': 'dir',
                      'images': {'thumb': thumb, 'fanart': fanart}})
#        thumb = host_url + qshow['images'][0]['url'] + '?lastWrite=&apikey={}'.format(api_key)
        #banner = host_url + show['images'][1]['url'] + '&apikey={}'.format(api_key)
#        fanart = host_url + qshow['images'][1]['url'] + '?lastWrite=&apikey={}'.format(api_key)


    xbmc.log( "LISTT: " + str(qnames))
    for show in data:
        name = show['title']
        down = str(show['downloaded'])
        if down == 'True':
            totalsize = show['movieFile']['size'] * 1e-9
            xbmc.log( "LISTT: " + str(totalsize))
            name += '   [COLOR FF3576F9]Downloaded[/COLOR] '
            width = str(show['movieFile']['mediaInfo']['width'])
            audiochan = str(show['movieFile']['mediaInfo']['audioChannels'])
            audiocodec = str(show['movieFile']['mediaInfo']['audioFormat'])
            if width == '1920':
                name += '[COLOR FF3576F9] 1080p[/COLOR] '
            if audiochan == '6':
                name += '[COLOR FF3576F9] 5.1[/COLOR] '
            name += '[COLOR FF3576F9] %s[/COLOR] ' % audiocodec
            name += ' [COLOR FF3576F9]  %sGB[/COLOR] ' % round(totalsize, 2)
            thumb = host_url + show['images'][0]['url'] + '?lastWrite=&apikey={}'.format(api_key)
            #banner = host_url + show['images'][1]['url'] + '&apikey={}'.format(api_key)
            fanart = host_url + show['images'][1]['url'] + '?lastWrite=&apikey={}'.format(api_key)
            show_id = show['id']
            seasons = 'na'
            dir_show = get_appended_path(dir_movies, str(show_id))
            file = 'seasons.json'
            file_path = get_appended_path(dir_show, file)
            write_json(file_path, seasons)
            shows.append({'name': name, 'url': str(show_id), 'mode': 'getMovie', 'type': 'dir',
                        'images': {'thumb': thumb, 'fanart': fanart}})

        else:
            if name in qnames:
                xbmc.log( "LISTT: SKIPPING " + str(name))
            else:
                name += '   [COLOR FFFF0000]Missing[/COLOR] '
                thumb = host_url + show['images'][0]['url'] + '?lastWrite=&apikey={}'.format(api_key)
                #banner = host_url + show['images'][1]['url'] + '&apikey={}'.format(api_key)
                fanart = host_url + show['images'][1]['url'] + '?lastWrite=&apikey={}'.format(api_key)
                show_id = show['id']
                seasons = 'na'
                dir_show = get_appended_path(dir_movies, str(show_id))
                file = 'seasons.json'
                file_path = get_appended_path(dir_show, file)
                write_json(file_path, seasons)
                shows.append({'name': name, 'url': str(show_id), 'mode': 'getMovie', 'type': 'dir',
                            'images': {'thumb': thumb, 'fanart': fanart}})


#                    name += '   [COLOR FFF7290A]Missing[/COLOR] '
    add_entries(shows)
    #Sort ignoring 'The'
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(pluginhandle)
    guiUpdateTimer = threading.Timer(
        60.0, # fire after  4 seconds
        refreshGuiItems)
    guiUpdateTimer.start()

def refreshGuiItems():
    xbmc.executebuiltin('Container.Refresh')


def get_movie(name, movie_id):
    dialog = xbmcgui.Dialog()
    #Show select dialog
    term = dialog.select('Radarr', ['Remove Movie from Watched List', 'Play Movie', 'Search for downloads'])
    #Remove from watched list
    if term is 0:
        snr.delete_movie(movie_id)
    #Play Movie
    if term is 1:
        data = snr.get_movie_by_id(movie_id)
        path = data['folderName']
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter": {"field": "path", "operator": "contains", "value": "%s"}, "properties" : ["file"]}, "id": 1}' % path)
        json_query = simplejson.loads(json_query)
        movid = json_query['result']['movies'][0]['movieid']
        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"movieid": %s}, "options":{ "resume":true }}, "id": 1}' % movid)
    #Search for downloads
    if term is 2:
        data = snr.get_movie_by_id(movie_id)
        xbmc.log("SEARCH : " + repr(data),level=2)
        search_individual(movie_id)


def get_all_movies():
    data = snr.get_movies()
    ord_data = sorted(data, key=lambda k: k['title'])   # order titles alphabetically
    list_movies(ord_data)

def get_queue():
    data = snr.get_queue()
    shows = []
    for show in data:
        name = show['movie']['title']
        try:
            thumb = show['movie']['images'][0]['url']
            fanart = show['movie']['images'][1]['url']
        except IndexError:
            thumb = ''
            fanart = ''
            xbmc.log("Radarr get_queue: Error setting Artwork...")
        totalsize = show['size'] * 1e-9
        perc = 100 - (100 * float(show['sizeleft'])/float(show['size']))
        name += '      [COLOR FF3576F9]%s%%[/COLOR] ' % round(perc, 1)
        name += ' [COLOR FF3576F9]of  %sGB[/COLOR] ' % round(totalsize, 2)
        show_id = show['id']
        seasons = 'na'
        dir_show = get_appended_path(dir_movies, str(show_id))
        file = 'seasons.json'
        file_path = get_appended_path(dir_show, file)
        write_json(file_path, seasons)
        shows.append({'name': name, 'url': str(show_id), 'mode': 'getShow', 'type': 'dir',
                      'images': {'thumb': thumb, 'fanart': fanart}})
    add_entries(shows)
    #Sort ignoring 'The'
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(pluginhandle)




params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
name = params.get('name')

xbmc.log("MODE : " + repr(mode), level=2)

if type(url) == type(str()):
    url = str(url)

if mode == None:
    root()
if mode == 'getAllMovies':
    get_all_movies()
elif mode == 'getMovie':
    get_movie(name, url)
elif mode == 'addMovie':
    add_movie(url)
elif mode == 'searchMissing':
    search_missing()
elif mode == 'getQueue':
    get_queue()
