# -*- coding: utf-8 -*-
'''
    redditbot.redditbot
'''

import irctk.bot
import irctk.plugins

import os
import time
import re
import yaml

from RedditBot.ircglob import glob
from RedditBot.utils import isignored, isadmin


class PluginHandler(irctk.plugins.PluginHandler):
    def enqueue_plugin(self, plugin, hook, context, regex=False):
        prefix = plugin['context']['prefix']
        if glob.is_valid(prefix) and isignored(prefix, self.bot) and not isadmin(prefix, self.bot):
            return
        super(PluginHandler, self).enqueue_plugin(plugin, hook, context, regex)

blacklist = ['REGEX', 'IGNORE', 'EVENTS', 'PLUGINS', 'START_TIME']

class Bot(irctk.bot.Bot):
    h_config = None
    data = {}

    def __init__(self):
        self.reply_hook = None
        super(Bot, self).__init__()
        self.plugin = PluginHandler(self)
    
    def save_config(self):
        with open('bot_config.yml', 'w') as f:
            f.write(yaml.dump(dict((key, value) for key, value in self.config.iteritems() if
                not (key.upper() in blacklist) and
                (not key in self.h_config or self.h_config[key] != value))))
    
    def load_config(self):
        if os.path.exists('bot_config.yml'):
            with open('bot_config.yml', 'r') as f:
                for key, value in yaml.load(f.read()).iteritems():
                    if not key in self.config or not self.config[key]:
                        self.config[key] = value
                    elif isinstance(self.config[key], list):
                        self.config[key] = list(set(self.config[key] + value))
    
    def set_reply_hook(self, hook):
        self.reply_hook = hook

    def reply(self, message, context, action=False, notice=False,
            recipient=None, line_limit=400, max_lines=3, **kwargs):
        # deal with reply hook for badwords
        if not kwargs.get('nofilter', False) and self.reply_hook:
            message = self.reply_hook(message)
        if not message:
            return
        
        message = message[:max_lines * line_limit]
        
        # split into lines
        for message in message.split('\n'):
            message = message.rstrip('\r')
            super(Bot, self).reply(message, context, action, notice, recipient, line_limit)
    
    def inject_input(self, line):
        self.irc.connection.inp.put(line + '\r\n')
    
    def _parse_input(self, wait=0.01):
        while True:
            time.sleep(wait)
            with self.irc.lock:
                prefix = self.config['CMD_PREFIX']
                
                args = self.irc.context.get('args')
                command = self.irc.context.get('command')
                message = self.irc.context.get('message')
                raw = self.irc.context.get('raw')
                
                while not self.context_stale and args:
                    
                    # process regex
                    for regex in self.config['REGEX']:
                        hook = regex['hook']
                        search = re.search(hook, args[-1])
                        if not search:
                            continue
                        regex['context'] = dict(self.irc.context)
                        regex['context']['regex_search'] = search
                        self.plugin.enqueue_plugin(regex,
                                                   hook,
                                                   args[-1],
                                                   regex=True)
                    
                    # process for a message
                    if message.startswith(prefix):
                        cmd = message[1:].split(' ')[0].lower()
                        match, exact, allmatches = False, False, []
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = dict(self.irc.context)
                            hook = plugin['hook'].lower()
                            if hook.startswith(cmd):
                                match = plugin
                                allmatches.append(plugin['hook'])
                                if hook == cmd:
                                    exact = plugin
                        if len(allmatches) > 1 and not exact:
                            if len(allmatches) < 4 and len(cmd) > 1:
                                self.reply('Not specific enough, did you mean: \x02{}\x02'.format('\x02, \x02'.join(allmatches)), self.irc.context)
                        else:
                            match = exact or match
                            if match:
                                hook = message.split(' ')[0]
                                self.plugin.enqueue_plugin(match, hook, message)
                    
                    # process for a command
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = dict(self.irc.context)
                            hook = event['hook']
                            self.plugin.enqueue_plugin(event, hook, command)
                    
                    # irc context consumed; mark it as such
                    self.irc.context['stale'] = True
