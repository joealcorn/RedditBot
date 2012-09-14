# -*- coding: utf-8 -*-
'''
    redditbot.redditbot
'''

import irctk.bot
import irctk.plugins

import importlib

from RedditBot.ircglob import glob
from RedditBot.utils import isignored, isadmin

class PluginHandler(irctk.plugins.PluginHandler):    
    def enqueue_plugin(self, plugin, hook, context, regex=False):
        importlib.import_module('RedditBot.utils')
        prefix = plugin['context']['prefix']
        if isignored(prefix, self.bot) and not isadmin(prefix, self.bot):
            return
        super(PluginHandler, self).enqueue_plugin(plugin, hook, context, regex)

class Bot(irctk.bot.Bot):
    def __init__(self):
        super(Bot, self).__init__()
        self.plugin = PluginHandler(self)
