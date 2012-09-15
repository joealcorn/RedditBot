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
        self.reply_hook = None
        super(Bot, self).__init__()
        self.plugin = PluginHandler(self)
    
    def set_reply_hook(self, hook):
        self.reply_hook = hook
    
    def reply(self, message, context, action=False, notice=False,
            recipient=None, line_limit=400, **kwargs):
        if not kwargs.get('nofilter', False) and self.reply_hook:
            message = self.reply_hook(message)
        if not message:
            return
        return super(Bot, self).reply(message, context, action, notice, recipient, line_limit)
