# Core
from datetime import datetime, date, timedelta, time
# Libs
import requests
from requests.auth import OAuth1
from clint.textui import puts, colored
# Project
import dtools


class DTTwitter(dtools.Plugin):

    def __init__(self):
        super(DTTwitter, self).__init__()
        # Urls used in the requests to twitter
        self.url = {
            'favs': 'http://api.twitter.com/1.1/favorites/list.json',
            'timeline': 'http://api.twitter.com/1.1/statuses/user_timeline.json'
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
        twitts = False
        favs = False
        yest = date.today() - timedelta(days=1)
        self.entries = [{'text': '', 'datetime': datetime.combine(yest, time.max)}]
        # Creating the import
        # for screen_name in self.config['screen_names']:
        for i in range(len(self.config['screen_names'])):
            screen_name = self.config['screen_names'][i]
            print "Checking for " + screen_name
            oauth = OAuth1(self.config['client_key'], self.config['client_key_secret'],
                            self.config['access_token'][i], self.config['access_token_secret'][i],
                            signature_type='auth_header')
            # Adding current screen name
            self.uparams['screen_name'] = screen_name
            # Sending the request
            r = requests.get(self.url['timeline'], params=self.uparams, auth=oauth)
            #print r.json
            for item in r.json:
                # Is it from yesterday?
                dt = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                post_date = dt.date()
                if yest != post_date:
                    continue
                # Checking if there is an image
                if self.__hasImage(item):
                    self.entries.append(self.__createPost(item))
                else:
                    twitts = True
                    self.entries[0]['text'] = self.__createPostItem(item) + self.entries[0]['text']
            # Create a favourites post
            if self.config['favorites']:
                r = requests.get(self.url['favs'], params=self.uparams, auth=oauth)
                fav_text = u''
                for item in r.json:
                    dt = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    post_date = dt.date()
                    if yest != post_date:
                        continue
                    favs = True
                    fav_text = self.__createPostItem(item) + fav_text  # Favs are not allowed their own entry
                if favs:
                    fav_text = u"### Favories\n\n" + fav_text
            else:
                fav_text = u''
        # Adding title
        self.entries[0]['text'] = "##Tweets for " + yest.strftime('%d-%m-%Y') + "\n" + self.entries[0]['text'] + fav_text
        if twitts:
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
