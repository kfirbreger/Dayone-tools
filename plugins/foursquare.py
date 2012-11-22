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
            "own_post_on_text": True,
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
        # Geting yest date
        yest = date.today() - timedelta(days=1)
        self.entries = []
        # For the daily summary reversing the order of import so that
        # the oldest will be at the top.
        for item in data.entries:
            entry_item = 0
            # Are we at yesterday?
            post_date = date(*item.published_parsed[:3])
            # If this is a post from today, or older then last run, ignore
            if yest < post_date:
                continue
            elif post_date < self.config['last_run'].date():
                continue
            elif post_date.strftime('%d-%m-%Y') not in dig_map:
                dig_map[post_date.strftime('%d-%m-%Y')] = entry_item = len(self.entries)
                self.entries.append({'text': '', 'datetime': datetime.combine(post_date, time.max)})
            else:
                entry_item = dig_map[post_date.strftime('%d-%m-%Y')]
            # Deciding if this deserves its own post
            if len(item.description) > (2 + len(item.title)):
                # Create an extra post?
                if self.config['own_post_on_text']:
                    self.entries.append({'text': self.__createPost(item), 'datetime': datetime(*item.published_parsed[:6])})
                else:
                    self.entries[entry_item]['text'] = "* " + self.__createPost(item) + "\n" + self.entries[entry_item]['text']
            else:
                self.entries[entry_item]['text'] = self.__createPostItem(item) + self.entries[entry_item]['text']
        # Adding digest header
        for k, v in dig_map.iteritems():
            self.entries[v]['text'] = u'## Foursquare checkins for ' + k + "\n" + self.entries[v]['text']
        # Create entries only if there actual entries
        if len(self.entries) > 0:
            self.writeToJournal()

    def __createPost(self, item):
        text = item.description[2:].split('-')
        text = u"[%s](%s) - %s" % (text[0], item.link, ''.join(text[1:]))
        return text

    def __createPostItem(self, item):
        return "* [%s](%s)\n" % (item.title, item.link)


def execute(dry=False):
    plugin = DTFourSquare()
    if dry:
        plugin.dryRun()
    plugin.run()
