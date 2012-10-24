
from RedditBot import bot, utils

import copy


blacklist = ['REGEX', 'IGNORE', 'EVENTS', 'PLUGINS', 'START_TIME']


@bot.command
def config(context):
    '''.config (list|view|set|add|remove|revert) <key> [value]'''
    if not utils.isadmin(context.line['prefix'], bot):
        return
    cmd = str(context.args).split(' ', 1)[0].lower()
    if not (cmd in ['list', 'set', 'add', 'remove', 'view', 'revert']):
        return
    if cmd == 'list':
        bot.reply(repr(bot.config.keys()), context.line, False, True, context.line['user'], nofilter=True)
        return
    cmd, key = str(context.args).split(' ', 1)
    if len(key.split(' ', 1)) > 1:
        key, arg = key.split(' ', 1)
    if key.upper() in blacklist:
        return
    if cmd == 'view':
        if key in bot.config and not key.upper().endswith(('_PASSWORD', '_KEY', 'TELL_DB')):
            bot.reply(repr(bot.config[key]), context.line, False, True, context.line['user'], nofilter=True)
        return
    elif cmd == 'revert':
        if key in bot.h_config:
            bot.config[key] = copy.deepcopy(bot.h_config[key])
            bot.save_config()
            bot.reply(repr(bot.config[key]), context.line, False, True, context.line['user'], nofilter=True)
        elif key in bot.config:
            del bot.config[key]
            bot.save_config()
            bot.reply('Key deleted.', context.line, False, True, context.line['user'], nofilter=True)
        else:
            bot.reply('Nothing to do.', context.line, False, True, context.line['user'], nofilter=True)
        return
    if cmd == 'set' and (not key in bot.config or isinstance(bot.config[key], str)):
        bot.config[key] = arg
        bot.save_config()
        return 'Set.'
    if key in bot.config and not isinstance(bot.config[key], list):
        return
    if not key in bot.config:
        bot.config[key] = []
    if cmd == 'add' and not arg in bot.config[key]:
        bot.config[key].append(arg)
        bot.save_config()
        return 'Added.'
    elif cmd == 'remove' and (not key in bot.h_config or not (arg in bot.h_config[key])):
        bot.config[key].remove(arg)
        if len(bot.config[key]) == 0 and not key in bot.h_config:
            del bot.config[key]
        bot.save_config()
        return 'Removed.'
