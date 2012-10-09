import simplejson as json


class Dayone:

    def __init__(self):
        pass

    def run(self):
        pass


class Plugin:

    def __init__(self):
        self.entries = []  # Hold the entries to be written

    # The following functions are required by all plugins
    def config(self):
        """
        The configure of this plugin. Needs to return the config.
        """
        pass

    def createConfigFile(self, config_dict):
        """
        Creates an empty config file based of the data of the plugin
        """
        json.dump(config_dict)

    def run(self):
        """
        Runs the plugin import.
        """
        pass

    def writeToJournal(self):
        """
        Writes the text to the journal. This should not be overwritten unkess you have a really good
        reason for it.
        It loops through the entries array and write them one by one, an entry is a dict of the following format:
        {
            datetime: The date and time to make the entry one
            title: Entry title
            text: The text for the entry
            image: An image file to add to the entry
            tags: Tags to add to the entry
            location: Add a location to the entry @TODO check if this is possible
        }
        """
        for entry in self.entries:
            print entry['title']
