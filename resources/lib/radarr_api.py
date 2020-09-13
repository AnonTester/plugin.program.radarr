# -*- coding: utf-8 -*-

import json
import requests
import xbmc

class RadarrAPI:
    # Radarr API
    host_url = ''
    api_key = ''

    def __init__(self, host_url, api_key):
        """Constructor requires Host-URL and API-KEY"""
        self.host_url = host_url
        self.api_key = api_key


    # ENDPOINT CALENDAR
    def get_calendar(self):
        # optional params: start (date) & end (date)
        """Gets upcoming episodes, if start/end are not supplied episodes airing today and tomorrow will be returned"""
        res = self.request_get("{}/calendar".format(self.host_url))
        return res.json()


    # ENDPOINT COMMAND


    # ENDPOINT DISKSPACE
    def get_diskspace(self):
        """Return Information about Diskspace"""
        res = self.request_get("{}/diskspace".format(self.host_url))
        return res.json()


    # ENDPOINT HISTORY
    # DOES NOT WORK
    def get_history(self):
        """Gets history (grabs/failures/completed)"""
        res = self.request_get("{}/history".format(self.host_url))
        return res.json()


    # ENDPOINT WANTED MISSING
    # DOES NOT WORK
    def search_missing(self, data):
        """Gets missing movies (movies without files)"""
        res = self.request_post("{}/command".format(self.host_url), data)
        return res.json()

    # ENDPOINT REFRESH MOVIE / SEARCH INDIVIDUAL
    def search_individual(self, data):
        xbmc.log("SEARCH : " + repr(data),level=2)
        """Refreshes movie and searches for updated versions"""
        #res = self.request_post("{}/command".format(self.host_url), data)
        res = self.request_post("{}/command".format(self.host_url), data)
        xbmc.log("SEARCH : " + repr(res),level=2)
        return res.json()

    # ENDPOINT QUEUE
    def get_queue(self):
        """Gets current downloading info"""
        res = self.request_get("{}/queue".format(self.host_url))
        return res.json()


    # ENDPOINT PROFILE
    def get_quality_profiles(self):
        """Gets all quality profiles"""
        res = self.request_get("{}/profile".format(self.host_url))
        return res.json()


    # ENDPOINT RELEASE


    # ENDPOINT RELEASE/PUSH


    # ENDPOINT ROOTFOLDER
    def get_root_folder(self):
        """Returns the Root Folder"""
        res = self.request_get("{}/rootfolder".format(self.host_url))
        return res.json()


    # ENDPOINT MOVIES
    def get_movies(self):
        """Return all movies in your collection"""
        res = self.request_get("{}/movie".format(self.host_url))
        return res.json()

    def get_movie_by_id(self, movie_id):
        """Return the movie with the matching ID or 404 if no matching series is found"""
        res = self.request_get("{}/movie/{}".format(self.host_url, movie_id))
        return res.json()

    def add_movie(self, data):
        """Add a new movie to your collection"""
        res = self.request_post("{}/movie".format(self.host_url), data)
        return res.json()

    def delete_movie(self, movie_id, rem_files=False):
        """Delete a movie from your collection"""
        data = {
            # 'id': series_id,
            'deleteFiles': 'false'
        }
        res = self.request_del("{}/movie/{}".format(self.host_url, movie_id), data)
        return res.json()






    # ENDPOINT MOVIE LOOKUP
    def lookup_movie(self, query):
        """Searches for new movie on trakt"""
        res = self.request_get("{}/movie/lookup?term={}".format(self.host_url, query))
        return res.json()

    # ENDPOINT SYSTEM-STATUS
    def get_system_status(self):
        """Returns the System Status"""
        res = self.request_get("{}/system/status".format(self.host_url))
        return res.json()

    # REQUESTS STUFF
    def request_get(self, url, data={}):
        """Wrapper on the requests.get"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.get(url, headers=headers, json=data)
        return res

    def request_post(self, url, data):
        """Wrapper on the requests.post"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.post(url, headers=headers, json=data)
        return res

    def request_put(self, url, data):
        """Wrapper on the requests.put"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.put(url, headers=headers, json=data)
        return res

    def request_del(self, url, data):
        """Wrapper on the requests.delete"""
        headers = {
            'X-Api-Key': self.api_key
        }
        res = requests.delete(url, headers=headers, json=data)
        return res
