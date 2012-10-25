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
            'last_run': "1970-01-01T00:00:00",
            'athlete_id': 0,
            'tags': ''
        }
        return conf

    def run(self):
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        if self.config['athlete_id'] == 0:
            puts(colored.yellow('Athlete id not set in config, skipping Strava'))
            return

        #now = datetime.now().strftime('%Y-%m-%d %H:%M')
        r = requests.get('http://www.strava.com/api/v1/rides', params={'athleteId': self.config['athlete_id']})
        for ride in r.json['rides']:
            ride_data = requests.get('http://www.strava.com/api/v1/rides/' + ride['id']).json
            # Checking if this is newer than last run
            ride_date = datetime.strpformat(ride_data['ride'])
            # If its an old entry move on
            if ride_date < self.config['last_run']:
                continue

            # Create a post


def execute(dry=False):
    plugin = DTStrava()
    if dry:
        plugin.dryRun()
    plugin.run()
