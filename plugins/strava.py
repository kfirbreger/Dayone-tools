# Core
from datetime import datetime, timedelta
import re
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
            ride_data = requests.get('http://www.strava.com/api/v1/rides/' + str(ride['id'])).json
            # Checking if this is newer than last run
            ride_date = datetime.strptime(ride_data['ride']['startDateLocal'][:-1], '%Y-%m-%dT%H:%M:%S')
            # If its an old entry move on
            if ride_date < self.config['last_run']:
                continue
            # Create a post
            self.entries.append(self.__createPost(ride_data['ride']))
        self.writeToJournal()

    def __createPost(self, item):
        post = {'datetime': datetime.strptime(item['startDateLocal'][:-1], '%Y-%m-%dT%H:%M:%S')}
        # Striping the date in the beginning if its there
        txt = "## " + re.sub(r'\d+/\d+/\d+', '', item['name']).strip() + "\n"
        if len(item['description']) > 0:
            txt += item['description'] + "\n"
        txt += "* Duration: " + str(timedelta(seconds=item['elapsedTime'])) + "\n"
        txt += "* Distance: %.2fkm\n" % (item['distance'] / 1000)
        txt += "* Average Speed: %.2fkm/h\n" % (item['averageSpeed'] * 3.6)  # Converting from m/s to km/h
        # avg power may be missing
        if item['averageWatts'] is not None:
            txt += "* Averge Watt: %.2fw\n" % item['averageWatts']
        txt += "* Elevation Gain: %dm\n" % int(item['elevationGain'])
        txt += "* Ridden on the %s\n" % item['bike']['name']
        txt += "* [link](http://app.strava.com/rides/%d)\n" % item['id']
        post['text'] = txt
        if len(self.config['tags']) > 0:
            post['text'] += "\n"
            post['tags'] = self.config['tags']
        return post


def execute(dry=False):
    plugin = DTStrava()
    if dry:
        plugin.dryRun()
    plugin.run()
