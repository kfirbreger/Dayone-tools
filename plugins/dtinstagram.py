import dtools
import simplejson as json


class DTInstagram(dtools.Plugin):

    client_id = 'Dayone Tools Instagram Plugin'
    client_secret = 'This_is_really_secure'

    def __init__(self):
        self.user_id = -1
        self.config_filename = 'instagram.json'
        self.access_token = None
        self.config = None

    def config(self):
        with open(self.config_filename) as conf_file:
            self.config = json.load(conf_file)
        if self.config is None:
            print "No settings file found"
            return False
        return True

    # Used if no access token is availble
    def getAccessToken(self):
        pass
