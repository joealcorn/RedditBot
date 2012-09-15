# ported from skybot

from RedditBot import bot, utils
from RedditBot.pastebin import paste

from itertools import imap

from datetime import datetime
import time

import sqlite3

def get_db_connection(name=None):
    if name is None:
        name = '{0}.{1}.db'.format(bot.config['NICK'], bot.config['SERVER'])
    return sqlite3.connect(name, timeout=10)


def db_init(db):
    db.execute('create table if not exists tell'
               '(id integer primary key asc, user_to, user_from, message, chan, time)')
    db.commit()


def get_tells(db, user_to):
    return db.execute('select user_from, message, time, chan from tell where'
                      ' user_to=lower(?) order by time',
                      (user_to.lower(),)).fetchall()

@bot.event('PRIVMSG')
def tellinput(context):
    nick = context.line['user']

    db = get_db_connection()
    db_init(db)

    tells = get_tells(db, nick)

    if len(tells) == 0:
        return

    reply = []
    for user_from, message, time, chan in tells:
        d_time = datetime.fromtimestamp(time)
        reply.append('{0} <{1}> {2}'.format(d_time.strftime('%H:%M'), user_from, message))

    if len(tells) > 2:
        p = paste('\n'.join(reply), 'Notes for {}'.format(nick))
        if p['success'] == True:
            db.execute('delete from tell where user_to=lower(?)', (nick,))
            db.commit()
        else:
            return

        return '{0}: See {1} for your messages.'.format(nick, p['url'])
    else:
        db.execute('delete from tell where user_to=lower(?)', (nick,))
        db.commit()
        return '\n'.join(imap(lambda x: '{0}: {1}'.format(nick, x), reply))

@bot.command
def tells(context):
    '''.tells <nick>'''
    if not utils.isadmin(context.line['prefix'], bot):
        return
    nick = context.args

    db = get_db_connection()
    db_init(db)

    tells = get_tells(db, nick)

    if len(tells) == 0:
        return

    db.execute('delete from tell where user_to=lower(?)', (nick,))
    db.commit()

    reply = []
    for user_from, message, time, chan in tells:
        d_time = datetime.fromtimestamp(time)
        reply.append('{0} <{1}> {2}'.format(d_time.strftime('%H:%M'), user_from, message))

    p = paste('\n'.join(reply), 'Notes for {}'.format(nick))
    if p['success'] == False:
        bot.reply('Could not paste notes', context.line, False, True, context.line['user'])
        return
    else:
        bot.reply(p['url'], context.line, False, True, context.line['user'])
        return


@bot.command
def tell(context):
    '''.tell <nick> <message>'''

    db = get_db_connection()
    db_init(db)

    query = context.args.split(' ', 1)
    nick = context.line['user']
    chan = context.line['sender']

    if len(query) != 2:
        return tell.__doc__

    user_to = query[0].lower()
    message = query[1].strip()
    user_from = nick

    if chan.lower() == user_from.lower():
        chan = 'a pm'

    if user_to == user_from.lower():
        return 'No.'

    #if db.execute('select count() from tell where user_to=?',
    #              (user_to,)).fetchone()[0] >= 5:
    #    return 'That person has too many things queued.'

    try:
        db.execute('insert into tell(user_to, user_from, message, chan, '
                   'time) values(?,?,?,?,?)', (user_to,
                                               user_from,
                                               message,
                                               chan,
                                               time.time()))
        db.commit()
    except db.IntegrityError:
        return 'Message has already been queued.'
    return '{0}: I\'ll tell {1} that when I see them.'.format(nick, user_to)
