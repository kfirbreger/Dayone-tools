# Core
from datetime import date, timedelta, datetime, time
#Libs
import feedparser
from clint.textui import puts, colored
# Project
import dtools


class DTFourSquare(dtools.Plugin):

    def __init__(self):
        super(DTFourSquare, self).__init__()
        self.config_filename = self.config_path + 'foursquare.json'
        self.entries = []
        # trying to load the config
        if not self.loadConfig():
            # There was no config file, creating it
            self.createConfigFile(self.getConfigDict(), self.config_filename)
            self.config = None

    def getConfigDict(self):
        conf = {
            "feed": "",
            "last_run": "1970-01-01T00:00:00",
            "import_images": False,
            "own_post_on_text": True,
            "tags": ""
        }
        return conf

    def run(self):
        data = None
        checkins = False  # Pessimism
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
        self.entries = [{'text': '## Foursquare checkins for ' + yest.strftime('%d-%m-%Y') + "\n", 'datetime': datetime.combine(yest, time.max)}]
        # Going through the entries, importing only items that are from yesterday
        # @TODO - Also do not import items before last run.
        for item in data.entries:
            # Are we at yesterday?
            post_date = date(*item.published_parsed[:3])
            # Date - date gives a timedelta object. We then call
            # its total seconds function to get seconds difference
            if int((yest - post_date).total_seconds()) != 0:
                continue
            # Deciding if this deserves its own post
            if self.config['own_post_on_text'] and (len(item.description) > (2 + len(item.title))):
                self.entries.append({'text': self.__createPost(item), 'datetime': datetime(*item.published_parsed[:6])})
            else:
                checkins = True
                self.entries[0]['text'] += self.__createPostItem(item)
        # Adding tags
        if len(self.config['tags']) > 0:
            for post in self.entries:
                post['text'] += "\n\n"
                post['tags'] = self.config['tags']
        # Removing first element if there are no global checkins in it
        if not checkins:
            self.entries = self.entries[1:]
        # Create entries only if there actual entries
        if len(self.entries) > 0:
            self.writeToJournal()

    def __createPost(self, item):
        text = item.description[2:]
        return text

    def __createPostItem(self, item):
        return "* [%s](%s)\n" % (item.title, item.link)


def execute(dry=False):
    plugin = DTFourSquare()
    if dry:
        plugin.dryRun()
    plugin.run()
