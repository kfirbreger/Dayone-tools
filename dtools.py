#!/usr/bin/env python

# Core
import json
import sys
import subprocess
from datetime import datetime
# Libs
from clint import args
from clint.textui import puts, colored, indent


class Dayone(object):

    def __init__(self):
        self.dry = False
        try:
            f = open('config.json')
            self.config = json.load(f)
        except:
            puts(colored.red('No cofig file found'))
            print sys.exc_info()[1]
            self.config = None

    def dryRun(self):
        """
        Sets the run to dry. This means everything will be done, but no entry will be created
        """
        self.dry = True

    def run(self, plugin_select=[]):
        if len(plugin_select) == 0:
            plugin_select = self.config['plugins']
        for plug in plugin_select:
            puts('Running ' + plug['name'])
            dtplugin = getattr(__import__("plugins", fromlist=[str(plug['name'])]), plug['name'])
            dtplugin.execute(self.dry)


class Plugin(object):

    def __init__(self):
        self.entries = []  # Hold the entries to be written
        self.config_path = 'plugins/'
        self.dry = False

    def dryRun(self):
        """
        Sets the run to dry. This means everything will be done, but no entry will be created
        """
        self.dry = True

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
        # Rendering the last run to a datetime
        if 'last_run' in self.config:
            self.config['last_run'] = datetime.strptime(self.config['last_run'], "%Y-%m-%dT%H:%M:%S")
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
            star: Should this be starred
        }
        """
        if 'last_run' in self.config:
            self.config['last_run'] = datetime.now().isoformat().split('.')[0]
        for entry in self.entries:
            print entry
            # Using a temp file to create an entry
            with open('tmpfile', 'w') as f:
                f.write(entry['text'].encode('UTF-8'))
                if 'tags' in entry:
                    f.write(entry['tags'] + "\n")
            cmd = 'dayone -d="' + entry['datetime'].strftime("%m/%d/%Y %l:%M%p") + '"'
            if 'image' in entry:
                cmd += ' --photo-file=' + entry['image']
            if 'star' in entry:
                cmd += ' --starred=true'
            cmd += ' new < tmpfile'
            puts(colored.blue(cmd))
            if not self.dry:
                subprocess.call(cmd, shell=True)
            # Removing created image
            if 'image' in entry:
                subprocess.call(['rm', entry['image']])

        # Cleaning up the tmpfile
        subprocess.call(['rm', 'tmpfile'])
        # Update last run only if this is not a dry run
        if 'last_run' in self.config and not self.dry:
            self.createConfigFile(self.config, self.config_filename)


if __name__ == '__main__':
    puts('Args are:')
    indent(4)
    puts(str(args.all))
    indent(-4)
    puts('Running')
    dt = Dayone()
    plugins = []
    for arg in args.all:
        if arg == '--dry':
            dt.dryRun()
        elif arg == '--help':
            print """
            Dayone import tool.
            Some more
            """
            exit()
        elif arg.startswith('--plugin'):
            plugins.append(arg.split('=')[1])
        else:
            puts(colored.red('Unknown arg %s terminating' % arg))
            exit()
    dt.run(plugins)
