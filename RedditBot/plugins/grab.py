
from RedditBot import bot
from RedditBot.pastebin import paste

import re

scrollback = {}

action_re = re.compile(r'^\x01ACTION (.*)\x01$', re.I)

@bot.event('PRIVMSG')
def add_to_scrollback(context):
    if not context.line['sender'].startswith('#'):
        return
    if context.line['message'].lower().startswith(bot.config['CMD_PREFIX'] + 'grab'):
        return
    if context.line['sender'].lower() not in scrollback:
        scrollback[context.line['sender'].lower()] = []
    s = scrollback[context.line['sender'].lower()]
    
    s.append((context.line['user'], context.line['message']))
    s[:] = s[-100:]

def format_line((user, message)):
    match = action_re.match(message)
    if match:
        return '* {0} {1}'.format(user, match.group(1))
    else:
        return '<{0}> {1}'.format(user, message)

@bot.command
def grab(context):
    '''.grab <start_text> [~~ <end_text>]'''
    if not context.line['sender'].startswith('#'):
        return
    if not context.line['sender'].lower() in scrollback:
        return 'Nothing found.'
    r = []
    if '~~' in context.args:
        str1, str2 = map(unicode.strip, context.args.lower().split('~~', 1))
        matched = False
        s = []
        for line in scrollback[context.line['sender'].lower()]:
            if str1 in line[1].lower():
                matched = True
            if matched:
                s.append(line)
                if str2 in line[1].lower():
                    r.extend(s)
                    s = []
                    break # make matching non-greedy, unsure if this is good thing
    else:
        str1 = context.args.lower().strip()
        for line in scrollback[context.line['sender'].lower()]:
            if str1 in line[1].lower():
                r[:] = [line]
                break
    if r == []:
        return 'Nothing found.'
    match = map(format_line, r)
    p = paste('\n'.join(match), title='Grabbed from {}'.format(context.line['sender']))
    if p['success']:
        return p['url']
    else:
        return 'Failed to paste'
