# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin
import sys
from urllib.parse import quote_plus

pluginhandle = int(sys.argv[1])

def add_entries(entries_list):
    entries = []
    is_folder = False
    for entry in entries_list:
        xbmc.log("ENTRYY " + str(entry))
        entry_name = entry['name']
        item = xbmcgui.ListItem(entry_name)
        item.setArt(entry.get('images'))
        entry_url = get_entry_url(entry)
        infolabels = entry.get('infoLabels')
        if entry['type'] == 'video':
            item.setInfo(type="video", infoLabels=infolabels)
            item.setProperty('IsPlayable', 'true')
            is_folder = False
        if entry['type'] == 'dir':
            item.setInfo(type="video", infoLabels={'title': entry_name})
            is_folder = True
        entries.append([entry_url, item, is_folder])
    xbmc.log( "ENTRIESS " + str(entries))
    xbmcplugin.addDirectoryItems(pluginhandle, entries)
    #Sort ignoring 'The'
#    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)




def get_entry_url(entry_dict):
    entry_url = sys.argv[0] + '?'
    if entry_dict is not {}:
        for param in entry_dict:
            if isinstance(entry_dict[param], str):
                entry_url += "%s=%s&" % (param, quote_plus(entry_dict[param]))
            elif isinstance(entry_dict[param], str):
                entry_url += "%s=%s&" % (param, quote_plus(entry_dict[param].encode('UTF-8')))
        if entry_url.endswith("&"):
            entry_url = entry_url[:-1]
    return entry_url


def parameters_string_to_dict(parameters):
    param_dict = {}
    if parameters:
        param_pairs = parameters[1:].split("&")
        for params_pair in param_pairs:
            param_splits = params_pair.split('=')
            if (len(param_splits)) == 2:
                param_dict[param_splits[0]] = param_splits[1]
    return param_dict
