# Core
from StringIO import StringIO
from datetime import datetime
# Libs
from instagram import client
from PIL import Image
import requests
# Project
import dtools


class DTInstagram(dtools.Plugin):

    def __init__(self):
        super(DTInstagram, self).__init__()
        self.config_filename = self.config_path + 'dtinstagram.json'
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            'client_id': '',
            'client_secret': '',
            'redirect_uri': '',
            'access_token': '',
            'tags': '',
            'last_run': "1970-01-01T00:00:00",
            'user_id': '',
            'like_fav_threshold': 10  # use -1 for never
        }
        return conf

    def getAccessToken(self):
        if not self.config:
            print "Trying to get access token before config. Stopping."
            return

        raw_scope = raw_input("Requested scope (separated by spaces, blank for just basic read): ").strip()
        scope = raw_scope.split(' ')
        # For basic, API seems to need to be set explicitly
        if not scope or scope == [""]:
            scope = ["basic"]

        api = client.InstagramAPI(client_id=self.config['client_id'], client_secret=self.config['client_secret'], redirect_uri=self.config['redirect_uri'])
        redirect_uri = api.get_authorize_login_url(scope=scope)

        print "Visit this page and authorize access in your browser:\n", redirect_uri

        code = raw_input("Paste in code in query string after redirect: ").strip()

        access_token = api.exchange_code_for_access_token(code)
        # Updating the data to include the access token and user id
        self.config['access_token'] = access_token[0]
        self.config['user_id'] = access_token[1]['id']
        # Saving the updated config
        self.createConfigFile(self.config, self.config_filename)

    def run(self):
        # All the access data is known, time to hit the server
        api = client.InstagramAPI(access_token=self.config['access_token'])
        recent_media, next = api.user_recent_media(count=20)
        # Creating posts
        for media in recent_media:
            post = self.__createPost(media)
            if len(self.config['tags']) > 0:
                post['tags'] = self.config['tags']
            # Checking if this is a new post
            delta = post['datetime'] - self.config['last_run']
            if delta.total_seconds() > 0:
                self.entries.append(post)
        # Timestamping last run
        self.config['datetime'] = datetime.now().isoformat()
        self.writeToJournal()
        self.createConfigFile(self.config, self.config_filename)

    def __createPost(self, media):
        post = {
            'text': str(media.caption)
        }
        # Getting instagram filename
        filename = media.images['standard_resolution'].url
        filename = filename.split('/')[-1]
        r = requests.get(media.images['standard_resolution'].url)
        i = Image.open(StringIO(r.content))
        i.save(filename)
        post['image'] = filename
        post['datetime'] = media.created_time
        # Marking as fav if above threshold
        if self.config['like_fav_threshold'] > -1:
            if len(media.likes) >= self.config['like_fav_threshold']:
                post['star'] = True
        return post


def execute(dry=False):
    plugin = DTInstagram()
    if dry:
        plugin.dryRun()
    if plugin.config['access_token'] == '':
        # No access Token, request one
        plugin.getAccessToken()
    plugin.run()
