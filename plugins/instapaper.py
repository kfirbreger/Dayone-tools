# Core
from datetime import date, timedelta, datetime, time
#Libs
import feedparser
from clint.textui import puts, colored
# Project
import dtools


class DTInstaPaper(dtools.Plugin):

    def __init__(self):
        super(DTInstaPaper, self).__init__()
        self.config_filename = self.config_path + 'instapaper.json'
        self.entries = []
        # trying to load the config
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            "feed": "",
            "tags": "",
            'last_run': "1970-01-01T00:00:00",
        }
        return conf

    def run(self):
        data = None
        if self.config is None:
            puts(colored.blue('Config file made, please fill in the required details'))
            return
        if len(self.config['feed']) == 0:
            puts(colored.yellow("No feed given"))
            return
        try:
            data = feedparser.parse(self.config['feed'])
        except:
            print "Error parsing feed " + self.config['feed']
            return
        if data.status != 200:
            print "Feed returned status " + str(data['status'])
            return
        # Creating digest map
        dig_map = {}
        # All is well, we can process
        # Geting yesterday's date
        yest = date.today() - timedelta(days=1)
        self.entries = []
        # Going through the entries, importing only items that are from yesterday
        # @TODO - Also do not import items before last run.
        for item in data.entries:
            # Are we at yesterday?
            post_date = date(*item.published_parsed[:3])
            if yest < post_date:
                continue
            elif post_date < self.config['last_run'].date():
                continue
            elif post_date.strftime('%d-%m-%Y') not in dig_map:
                dig_map[post_date.strftime('%d-%m-%Y')] = entry_item = len(self.entries)
                self.entries.append({'text': '## Saved to Instapaper on ' + post_date.strftime('%d-%m-%Y') + "\n", 'datetime': datetime.combine(post_date, time.max)})
            else:
                entry_item = dig_map[post_date.strftime('%d-%m-%Y')]
            self.entries[entry_item]['text'] += self.__createPostEntry(item)

        if len(self.entries) > 0:
            self.writeToJournal()

    def __createPostEntry(self, item):
        return "* [%s](%s)\n" % (item.title, item.link)


def execute(dry=False):
    plugin = DTInstaPaper()
    if dry:
        plugin.dryRun()
    plugin.run()
