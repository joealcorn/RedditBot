
from RedditBot import bot, utils
from RedditBot.ircglob import glob

from itertools import groupby, ifilter, ifilterfalse, imap

import __builtin__
import sys
import threading
import os.path

save_ignores_lock = threading.Lock()

def save_ignores():
    print 'Saving the ignore list...'
    with save_ignores_lock:
        with open('bot_ignore.txt', 'w') as f:
            f.writelines(utils.newlines(bot.config.setdefault('IGNORE', [])))

if os.path.exists('bot_ignore.txt'):
    with open('bot_ignore.txt', 'r') as f:
        bot.config['IGNORE'] = utils.stripnewlines(f.readlines())

@bot.command('.')
@bot.command('help')
@bot.command
def usage(context):
    '''.usage <plugin>'''
    plugin = context.args
    if plugin:
        for p in bot.config['PLUGINS']:
            if plugin == p['hook']:
                return p['funcs'][0].__doc__
    else:
        p = [(p['hook'], p['funcs']) for p in bot.config['PLUGINS']]
        p.sort(key=lambda t: t[1])
        result = []
        # group by function
        for k, v in groupby(p, key=lambda t: t[1]):
            grouped = [v[0] for v in v]
            grouped[0] = '\x02' + grouped[0] + '\x02'
            if len(grouped) > 1:
                # shortcuts/secondary
                for i, hook in enumerate(grouped[1:]):
                    grouped[i+1] = '[' + grouped[i+1] + ']'
            result.append(' '.join(grouped))
        result.sort()
        p = ', '.join(result)
        return 'Plugins currently loaded: ' + p

@bot.command
def raw(context):
    '''.raw <command>'''
    #if not context.line['prefix'] in bot.config.get('ADMINS', []):
    #    return
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if context.args:
        command = context.args.split(' ', 1)[0]
        args = list(context.args.split(' ', 1)[-1])
        bot.irc.send_command(command, args)
    else:
        return raw.__doc__

@bot.command
def eval(context):
    '''.eval <command>'''
    #if not context.line['prefix'] in bot.config.get('ADMINS', []):
    #    return
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if context.args:
        try:
            return str(__builtin__.eval(context.args))
        except:
            return repr(sys.exc_info()[1])
    else:
        return eval.__doc__

@bot.command
def ignore(context):
    '''.ignore nick!user@host'''
    bot.config.setdefault('IGNORE', [])
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if context.args:
        to_ignore = glob(context.args)
        supersets = list(ifilter(lambda ignored: to_ignore.issub(glob(ignored)), bot.config['IGNORE']))
        if len(supersets) > 0:
            return 'Not ignoring \x02%s\x02 because it is already matched by \x02%s\x02' % (context.args, supersets[0])
        
        filter = lambda ignored: to_ignore.issuper(glob(ignored))
        removed = list(ifilter(filter, bot.config['IGNORE']))
        
        bot.config['IGNORE'] = list(ifilterfalse(filter, bot.config['IGNORE']))
        bot.config['IGNORE'].append(context.args)
        
        save_ignores()
        
        if len(removed) > 0:
            return 'Ignored and removed \x02%d\x02 redundant ignores: \x02%s\x02' % (len(removed), '\x02, \x02'.join(removed))
        else:
            return 'Ignored.'
    else:
        return eval.__doc__

@bot.command
def unignore(context):
    '''.unignore nick!user@host'''
    bot.config.setdefault('IGNORE', [])
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if context.args:
        to_unignore = glob(context.args)
        
        filter = lambda ignored: to_unignore.issuper(glob(ignored))
        subsets = list(ifilter(filter, bot.config['IGNORE']))
        if len(subsets) == 0:
            return 'Nothing to unignore.'
        
        bot.config['IGNORE'] = list(ifilterfalse(filter, bot.config['IGNORE']))
        
        save_ignores()
        
        return 'Removed \x02%d\x02 ignores: \x02%s\x02' % (len(subsets), '\x02, \x02'.join(subsets))
    else:
        return eval.__doc__
