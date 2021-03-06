# Core
from datetime import datetime, date, timedelta, time
# Libs
import requests
from requests_oauthlib import OAuth1
from clint.textui import puts, colored
# Project
import dtools


class DTTwitter(dtools.Plugin):

    def __init__(self):
        super(DTTwitter, self).__init__()
        # Urls used in the requests to twitter
        self.url = {
            'favs': 'https://api.twitter.com/1.1/favorites/list.json',
            'timeline': 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        }
        # General params to send with the request
        self.uparams = {
            'count': 200,
            'screen_name': None,
            'exclude_replies': True,
            'include_entities': True
        }
        self.config_filename = self.config_path + 'twitter.json'
        # trying to load the config
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            'screen_names': [],
            'last_run': "1970-01-01T00:00:00",
            'import_images': False,
            'favorites': True,
            'retweet': True,
            # Replaces the twitter shortend URL with the original
            # Note that this can make the acual text longer then 140 chars.
            'replace_short_url': True,
            'tags': '',
            # As of 1.1 twitter requires OAuth for everything
            # Per screen name there is an access token and secret
            'access_token': [],
            'access_token_secret': [],
            'client_key': '',
            'client_key_secret': '',
        }
        return conf

    def run(self):
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        # Geting yesterday's date
        # Creating digest map
        dig_map = {}
        yest = date.today() - timedelta(days=1)
        self.entries = []
        # Creating the import
        # for screen_name in self.config['screen_names']:
        for i in range(len(self.config['screen_names'])):
            screen_name = self.config['screen_names'][i]
            print "Checking for " + screen_name
            headerauth = OAuth1(self.config['client_key'], self.config['client_key_secret'],
                            self.config['access_token'][i], self.config['access_token_secret'][i],
                            signature_type='auth_header')
            # Adding current screen name
            self.uparams['screen_name'] = screen_name
            # Sending the request
            r = requests.get(self.url['timeline'], params=self.uparams, auth=headerauth)
            for item in r.json():
                entry_item = 0
                # Is it from yesterday?
                dt = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                post_date = dt.date()
                if yest < post_date:
                    continue
                elif post_date < self.config['last_run'].date():
                    continue
                elif post_date.strftime('%d-%m-%Y') not in dig_map:
                    dig_map[post_date.strftime('%d-%m-%Y')] = entry_item = len(self.entries)
                    self.entries.append({'text': '', 'datetime': datetime.combine(post_date, time.max)})
                else:
                    entry_item = dig_map[post_date.strftime('%d-%m-%Y')]
                # Checking if there is an image
                if self.__hasImage(item):
                    self.entries.append(self.__createPost(item))
                else:
                    self.entries[entry_item]['text'] = self.__createPostItem(item) + self.entries[entry_item]['text']
            # Create a favourites post
            # Not yet figured a good solution for this, so taking favs out for now
            if self.config['favorites']:
                r = requests.get(self.url['favs'], params=self.uparams, auth=headerauth)
                fav_text = u''
                for item in r.json():
                    dt = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    post_date = dt.date()
                    if yest != post_date:
                        continue
                    fav_text = self.__createPostItem(item) + fav_text  # Favs are not allowed their own entry

        # Adding title
        for k, v in dig_map.iteritems():
            self.entries[v]['text'] = "## Tweets for " + k + "\n" + self.entries[v]['text']
        if len(self.entries) > 0:
            self.writeToJournal()

    def __createPostItem(self, item):
        """
        Creates an entry from a tweet. Each tweet gets its own unordered list item if no media is present.
        If the tweet has its own image, and allow_own is True it gets its own entry.
        """
        # @TODO Check for media and if needed add to own_entries
        p = item['created_at'].find(':')
        post_time = item['created_at'][p - 2: p + 3]
        item_url = u"https://twitter.com/" + unicode(item['user']['screen_name']) + u"/status/" + unicode(item['id'])
        # Changing new line for space so that markdown stays good.
        txt = item['text'].replace("\n", " ")
        # Making links actually link
        for link in item['entities']['urls']:
            new_url = link['url']
            if self.config['replace_short_url']:
                new_url = link['expanded_url']
            txt = txt.replace(link['url'], u'[' + new_url + u'](' + new_url + u')')

        return "* [%s](%s) %s\n" % (post_time, item_url, txt)

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


def execute(dry=False):
    plugin = DTTwitter()
    if dry:
        plugin.dryRun()
    plugin.run()
