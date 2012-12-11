# -*- coding: utf-8 -*-
'''
    redditbot.redditbot
'''

import irctk.bot
import irctk.plugins

import inspect
import os
import re
import sys
import time
import traceback
import yaml

from RedditBot.ircglob import glob
from RedditBot.utils import isignored, isadmin
from RedditBot.pastebin import paste


class PluginHandler(irctk.plugins.PluginHandler):
    def enqueue_plugin(self, plugin, hook, context, regex=False):
        prefix = plugin['context']['prefix']
        if glob.is_valid(prefix) and isignored(prefix, self.bot) and not isadmin(prefix, self.bot):
            return
        super(PluginHandler, self).enqueue_plugin(plugin, hook, context, regex)

    # unfortunately we have to override this to catch an exception at func()
    def dequeue_plugin(self, plugin, plugin_context):
        for func in plugin['funcs']:
            takes_args = inspect.getargspec(func).args

            action = False
            if plugin.get('action'):
                action = True

            notice = False
            if plugin.get('notice'):
                notice = True

            try:
                if takes_args:
                    message = func(plugin_context)
                else:
                    message = func()
            except:
                etype = sys.exc_info()[0]
                plg = func.__module__
                full = ''.join(traceback.format_exception(*sys.exc_info()))
                baby = ''.join(traceback.format_tb(sys.exc_info()[2], 1)).split('\n')

                sys.stderr.write(full)

                if not self.config['SNOOP_CHANNEL']:
                    return

                try:
                    p = paste(full, title='Internal {0}'.format(etype.__name__), unlisted=1, language='pytraceback')
                    if p['success']:
                        self.bot.log((plg, 'EXCEPTION'), etype.__name__, p['url'])
                    else:
                        self.bot.log((plg, 'EXCEPTION', 'PASTE_FAILED'), p['error'])
                        raise Exception()
                except:
                    self.bot.log((plg, 'EXCEPTION', 'PASTE_FAILED'), etype.__name__, baby)
                return

            if message:
                self._reply(message, plugin_context.line, action, notice)

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

    def format_for_log(self, thing):
        if isinstance(thing, basestring):
            return thing
        elif isinstance(thing, irctk.plugins.Context):
            return u'\x02{0}\x02'.format(thing.line['user'])
        elif isinstance(thing, dict):
            return u' '.join(u'{0}={1}'.format(*item) for item in thing.items())
        elif isinstance(thing, tuple):
            return u':'.join(thing)
        elif isinstance(thing, list):
            return u', '.join(thing)
        else:
            return unicode(thing)

    def log(self, *args):
        if not self.config['SNOOP_CHANNEL']:
            return
        self.irc.send_message(self.config['SNOOP_CHANNEL'], u' '.join(self.format_for_log(x) for x in args))

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
