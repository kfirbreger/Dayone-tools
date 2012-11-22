# Dayone Social Tools
A series of scripts ment to import entries from different social networks. If you do not have the dayone cli installed, this will not work.

**Important:** This is still in alpha and therefore include a lot of debugging information.
## Usage

    dtools.py

This will read the plugins in the config and will run them one by one.
There are several flags you can give the cl:

* <code>--dry</code> Make a dry run
* <code>--help</code> Display cl information
* <code>--plugin=PLUGIN-NAME</code> Runs only that plugin

At the first run of each plugin a config file will be created

### Dry run
A dry run will do everything and print out the command about to be run, but will not actually execute this command. A dry run also does not update the last_run setting in the config/

### Tags
As of 1.9 Dayone supports tags. Since the CLI as of yet does not support it, after the entry is created the tags are injected directly into the plist

## Plugins
For each social network there is a plugin py file and a settings file. All settings are JSON based. Feel free to add your own plugin

### Instagram
Instagram requires the use of OAuth. I am not adding my own app clients credentials. To use the instagram plugin you will need to create an app client on their site[^1] and fill in the information in the config file. The plugin does support getting a token for your user once you have the app credentials

### Twitter ###
As of API 1.1 twitter also requires authentication on every call. You will need to generate your own keys.

## Future updates
At the moment only foursquare and instagram are supported. future updates will include:

* General atom/rss feed
* Facebook statues

[^1]: This is quite easy to do and does not take more then 5 minutes to setup.