# Core
from datetime import date, datetime, timedelta, time
# Libs
import requests
from clint.textui import puts, colored
# Project
import dtools


class DTGitHub(dtools.Plugin):

    def __init__(self):
        super(DTGitHub, self).__init__()
        self.config_filename = self.config_path + 'github.json'
        self.entries = []
        # trying to load the config
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            "username": "",
            "tags": "",
            'last_run': "1970-01-01T00:00:00",
        }
        return conf

    def run(self):
        entry_item = 0
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        elif self.config['username'] == "":
            puts(colored.yellow('No username in config file'))
            return
        # Creating digest map
        dig_map = {}
        yest = date.today() - timedelta(days=1)
        self.entries = []
        r = requests.get('https://github.com/' + self.config['username'] + '.json')
        for item in r.json:
            # Checking of this is a post
            created = self.__parseDateTime(item['created_at'])
            post_date = created.date()
            if yest < post_date:
                continue
            elif post_date < self.config['last_run'].date():
                continue
            elif post_date.strftime('%d-%m-%Y') not in dig_map:
                dig_map[post_date.strftime('%d-%m-%Y')] = entry_item = len(self.entries)
                self.entries.append({'text': '## Github activity for ' + post_date.strftime('%d-%m-%Y') + "\n", 'datetime': datetime.combine(post_date, time.max)})
            else:
                entry_item = dig_map[post_date.strftime('%d-%m-%Y')]
            # Adding appropriate entry
            txt = self.__createPostItem(item, post_date.strftime('%Y-%m-%d %H:%M'))
            if txt is not None:
                self.entries[entry_item]['text'] += txt
        # Add entry if something happend yesterday
        if len(self.entries) > 0:
            self.writeToJournal()

    def __createPostItem(self, item, created):
        txt = None
        if item['type'] == u'CreateEvent':
            txt = "* [%s](%s) repository %s created\n" % (created, item['repository']['url'], item['repository']['name'])
        if item['type'] == u"PushEvent":
            ref = item['payload']['ref'].replace('refs/', '').replace('heads/', '')
            txt = "* [%s](%s) Pushed to branch *%s* of %s\n" % (created, item['repository']['url'], ref, item['repository']['name'])
        if item['type'] == u"GistEvent":
            txt = "* [%s](%s) Created gist %s\n" % (created, item['payload']['url'], item['payload']['name'])
        if item['type'] == u"WatchEvent":
            if item['payload']['action'] == "started":
                txt = "* %s Started watching [%s](%s)\n" % (created, item['repository']['name'], item['repository']['url'])
        return txt

    def __parseDateTime(self, dt_string):
        offset = 0
        try:
            offset = int(dt_string[-6:].replace(':', ''))
        except:
            print "Error"

        delta = timedelta(hours=(offset / 100))
        time = datetime.strptime(dt_string[:-6], '%Y-%m-%dT%H:%M:%S')
        time -= delta
        return time


def execute(dry=False):
    plugin = DTGitHub()
    if dry:
        plugin.dryRun()
    plugin.run()
