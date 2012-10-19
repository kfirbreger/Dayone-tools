# Core
import datetime
# Libs
import requests
from clint.textui import puts, colored
# Project
import dtools


class DTTwitter(dtools.Plugin):

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
        self.config_filename = self.config_path + 'twitter.json'
        # trying to load the config
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict)
            self.config = None

    def getConfigDict(self):
        conf = {
            'screen_names': [],
            'last_run': 0,
            'import_images': False,
            'favorites': True,
            'retweet': True,
            'tags': '',
            # As of 1.1 twitter requires OAuth for everything
            'access_token': '',
            'access_token_secret': ''
        }
        return conf

    def run(self):
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        now = datetime.now()
        # Posts contains the posts to make. The first element is the general twit post
        # The rest will be image including individual images
        posts = ["##Tweets from " + self.conf['last_run'] + " till " + now + "\n\n"]
        # Creating the import
        for screen_name in self.config['screen_names']:
            # Adding current screen name
            self.uparams['screen_name'] = screen_name
            # Sending the request
            r = requests.get(self.timeline, params=self.uparams)
            for item in r.json:
                # Checking if there is an image
                if self.__hasImage(item):
                    posts.append(self.__createPost(item))
                else:
                    posts[0] += self.__createPostItem(item)
            # Create a favourites post
            if self.uparams['favorites']:
                r = requests.get(self.favs, params=self.uparams)
                for item in r.json:
                    posts[0] += self.__createPostItem(item)  # Favs are not allowed their own entry

    def __createPostItem(self, item):
        """
        Creates an entry from a tweet. Each tweet gets its own unordered list item if no media is present.
        If the tweet has its own image, and allow_own is True it gets its own entry.
        """
        # @TODO Check for media and if needed add to own_entries
        p = item['created_at'].find(':')
        post_time = item['created_at'][p - 2: p + 3]
        item_url = "https://twitter.com/" + item['user']['screen_name'] + " /status/" + item['id_str']
        return "* [%s](%s) %s" % (post_time, item_url, item['text'])

    def __hasImage(self, item):
        """
        Checks to see if the post has an image embedded in it.
        """
        return False

    def __createPost(self, item):
        """
        Creates a post from the twit with the image
        """
        pass
