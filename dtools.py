#!/usr/bin/env python

# Core
import json
import sys
import subprocess
# Libs
from clint import args
from clint.textui import puts, colored, indent


class Dayone(object):

    def __init__(self):
        try:
            f = open('config.json')
            self.config = json.load(f)
        except:
            puts(colored.red('No cofig file found'))
            print sys.exc_info()[1]
            self.config = None

    def run(self):
        puts(unicode(self.config))
        for plug in self.config['plugins']:
            puts('Running ' + plug['name'])
            dtplugin = getattr(__import__("plugins", fromlist=[str(plug['name'])]), plug['name'])
            dtplugin.execute()


class Plugin(object):

    def __init__(self):
        self.entries = []  # Hold the entries to be written
        self.config_path = 'plugins/'

    # The following functions are required by all plugins
    def loadConfig(self):
        """
        The configure of this plugin. Needs to return the config.
        """
        try:
            with open(self.config_filename) as conf_file:
                self.config = json.load(conf_file)
        except:
            puts(colored.red(str(sys.exc_info()[1])))
            return False
        if self.config is None:
            puts(colored.red("No settings file found"))
            return False
        return True

    def createConfigFile(self, config_dict, filename):
        """
        Creates an empty config file based of the data of the plugin
        """
        f = open(filename, 'w')
        json.dump(config_dict, f, indent=4)

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
            text: The text for the entry
            image: An image file to add to the entry
            tags: Tags to add to the entry
            location: Add a location to the entry @TODO check if this is possible
        }
        """
        for entry in self.entries:
            # Using a temp file to create an entry
            with open('tmpfile', 'w') as f:
                f.write(entry['text'])
                if 'tags' in entry:
                    f.write(entry['tags'] + "\n")
            cmd = 'dayone -d="' + entry['datetime'].strftime("%m/%d/%Y %l:%M%p") + '" new < tmpfile'
            puts(colored.blue(cmd))
            subprocess.call(cmd, shell=True)

        # Cleaning up the tmpfile
        subprocess.call(['rm', 'tmpfile'])


if __name__ == '__main__':
    puts('Args are:')
    indent(4)
    puts(str(args.all))
    indent(-4)
    puts('Running')
    dt = Dayone()
    dt.run()
