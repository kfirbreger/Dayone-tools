# Core
import json
import datetime
# Libs
import requests
# Project
import dttools


class DTTwitter(dttools.Plugin):

    def __init__(self):
        # Urls used in the requests to twitter
        self.url = {
            'favs': 'http://api.twitter.com/1/favorites.json',
            'timeline': 'http://api.twitter.com/1/statuses/user_timeline.json'
        }
        # General params to send with the request
        self.uparams = {
            'count': 200,
            'screen_name': None,
            'exclude_replies': True,
            'include_entities': True
        }
        # Tweets that will get their own entry
        self.own_entries = []
        self.config_filename = 'twitter.json'
        # trying to load the config
        if not self.config():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict)

    def config(self):
        with open(self.config_filename) as conf_file:
            self.config = json.load(conf_file)
        if self.config is None:
            print "No settings file found"
            return False
        return True

    def getConfigDict(self):
        conf = {
            'screen_names': [],
            'last_run': 0,
            'import_images': False,
            'favorites': True,
            'retweet': True,
            'tags': ''
        }
        return conf

    def run(self):
        if not self.config():
            return False
        now = datetime.now()
        post = "##Tweets from " + self.conf['last_run'] + " till " + now + "\n\n"
        # Creating the import
        for screen_name in self.config['screen_names']:
            # Adding current screen name
            self.uparams['screen_name'] = screen_name
            # Sending the request
            r = requests.get(self.timeline, params=self.uparams)
            for item in r.json:
                post += self.__createPostItem(item)
            # Create a favourites post
            if self.uparams['favorites']:
                r = requests.get(self.favs, params=self.uparams)
                for item in r.json:
                    post += self.__createPostItem(item, False)  # Favs are not allowed their own entry

    def __createPostItem(self, item, allow_own=True):
        """
        Creates an entry from a tweet. Each tweet gets its own unordered list item if no media is present.
        If the tweet has its own image, and allow_own is True it gets its own entry.
        """
        # @TODO Check for media and if needed add to own_entries
        return "* " + item.text + "\n"
