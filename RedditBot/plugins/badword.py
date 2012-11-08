
from RedditBot import bot, utils

from itertools import ifilter, imap

import re
import os
import threading

badwords = []

save_badwords_lock = threading.Lock()

def save_badwords():
    global badwords
    print 'Saving the badword list...'
    with save_badwords_lock:
        with open('bot_badword.txt', 'w') as f:
            f.writelines(utils.newlines(badwords))

if os.path.exists('bot_badword.txt'):
    with open('bot_badword.txt', 'r') as f:
        badwords = utils.stripnewlines(f.readlines())

def reply_hook(message):
    bad_re = list(imap(lambda x: re.compile(re.escape(x), re.I), badwords))
    for word in bad_re:
        message = word.sub('[BADWORD]', message)
    return message

bot.set_reply_hook(reply_hook)

@bot.command
def addbadword(context):
    '''.addbadword <word>'''
    global badwords
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if any(imap(lambda word: word in context.args.lower(), badwords)):
        return 'This would be redundant, not adding.'
    removed = list(ifilter(lambda word: context.args.lower() in word, badwords))
    badwords = list(ifilter(lambda word: not (context.args.lower() in word), badwords))
    badwords.append(context.args.lower())
    save_badwords()
    if len(removed) > 0:
        bot.reply('Removed \x02%d\x02 redundant badwords: \x02%s\x02' % (len(removed), '\x02, \x02'.join(removed)),
            context.line, False, True, context.line['user'], nofilter = True)
    bot.log(context.line, 'BADWORD', 'ADD', context.args)
    return 'Added.'

@bot.command
def delbadword(context):
    '''.delbadword <word>'''
    global badwords
    if not utils.isadmin(context.line['prefix'], bot):
        return
    old = len(badwords)
    badwords = list(ifilter(lambda word: word != context.args.lower(), badwords))
    save_badwords()
    bot.log(context.line, 'BADWORD', 'DEL', context.args)
    return 'Removed \x02%d\x02 badwords.' % (old - len(badwords))

@bot.command
def listbadwords(context):
    '''.listbadwords'''
    global badwords
    if not utils.isadmin(context.line['prefix'], bot):
        return
    word_list = list(badwords)
    if len(word_list) == 0:
        bot.reply('Nothing to list.', context.line, False, True, context.line['user'], nofilter = True)
    next, word_list = word_list[:4], word_list[4:]
    while next:
        bot.reply('\x02%s\x02' % '\x02, \x02'.join(next), context.line, False, True, context.line['user'], nofilter = True)
        next, word_list = word_list[:4], word_list[4:]
