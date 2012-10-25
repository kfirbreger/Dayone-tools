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
            "tags": ""
        }
        return conf

    def run(self):
        data = None
        saved_for_later = False  # Pessimism
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
        # All is well, we can process
        # Geting yesterday's date
        yest = date.today() - timedelta(days=1)
        self.entries = [{'text': '## Saved to Instapaper on ' + yest.strftime('%d-%m-%Y') + "\n", 'datetime': datetime.combine(yest, time.max)}]
        # Going through the entries, importing only items that are from yesterday
        # @TODO - Also do not import items before last run.
        for item in data.entries:
            # Are we at yesterday?
            post_date = date(*item.published_parsed[:3])
            # Date - date gives a timedelta object. We then call
            # its total seconds function to get seconds difference
            if yest != post_date:
                continue
            # Deciding if this deserves its own post
            saved_for_later = True
            self.entries[0]['text'] += self.__createPostEntry(item)

        if saved_for_later:
            self.writeToJournal()

    def __createPostEntry(self, item):
        return "* [%s](%s)\n" % (item.title, item.link)


def execute(dry=False):
    plugin = DTInstaPaper()
    if dry:
        plugin.dryRun()
    plugin.run()
