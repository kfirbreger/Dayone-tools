# Core
from datetime import datetime
# Libs
import requests
from clint.textui import puts, colored
# Project
import dtools


class DTStrava(dtools.Plugin):

    def __init__(self):
        super(DTStrava, self).__init__()
        self.url = {
            'activities': 'http://api.strava.com/v1'
        }
        self.config_filename = self.config_path + 'strava.json'
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            'last_run': 0,
            'uid': 0,
            'tags': ''
        }
        return conf

    def run(self):
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M')


def execute(dry=False):
    plugin = DTStrava()
    if dry:
        plugin.dryRun()
    plugin.run()
