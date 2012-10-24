from RedditBot import bot
from RedditBot.utils import generate_insult
from RedditBot.pastebin import paste

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from datetime import datetime


engine = create_engine(bot.config['TELL_DB'], echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class tells(Base):
    __tablename__ = 'tells'

    id = Column(Integer, primary_key=True)
    user_to = Column(String(50))
    user_from = Column(String(50))
    message = Column(String(512))
    channel = Column(String(50))
    time = Column(DateTime)

    def __init__(self, user_to, user_from, message, channel):
        self.user_to = user_to
        self.user_from = user_from
        self.message = message
        self.channel = channel
        self.time = datetime.utcnow()


def get_users():
    session = Session()
    users = session.query(tells.user_to).distinct()
    bot.data['TELL_USERS'] = [u.user_to for u in users]


def make_date_string(date):
    if date.day != datetime.utcnow().day:
        return date.strftime('%d %b %H:%M')
    else:
        return date.strftime('%H:%M')


@bot.command('tell')
def new_tell(context):
    '''.tell <nick> <message>'''

    query = context.args.split(' ', 1)
    user_from = context.line['user']
    channel = context.line['sender']

    if len(query) != 2:
        return new_tell.__doc__

    user_to = query[0].lower()
    message = query[1].strip()

    if user_to == user_from.lower():
        return 'You can tell yourself that, you {0}.'.format(generate_insult())
    elif user_to == bot.irc.nick.lower():
        return 'No, you {0}.'.format(generate_insult())

    if channel.lower() == user_from.lower():
        channel = 'a pm'

    session = Session()

    t = tells(user_to, user_from, message, channel)
    session.add(t)
    session.commit()
    Session.remove()
    get_users()

    return u'{0}: I\'ll tell {1} that when I see them.'.format(
             user_from, user_to)


@bot.event('PRIVMSG')
def tell_user(context):
    nick = context.line['user']

    if nick.lower() not in bot.data['TELL_USERS']:
        return

    session = Session()
    messages = session.query(tells).filter_by(user_to=nick.lower()).all()

    if not messages:
        Session.remove()
        return

    msgs = [u'{0} <{1}> {2}'.format(make_date_string(message.time),
             message.user_from, message.message) for message in messages]

    if len(msgs) > 2:
        p = paste('\n'.join(msgs), u'Notes for {0}'.format(nick))

        if p['success']:
            map(session.delete, messages)
            session.commit()
            Session.remove()
            get_users()
            return u'{0}: See {1} for your messages'.format(nick, p['url'])
        else:
            Session.remove()
            return
    else:
        map(session.delete, messages)
        session.commit()
        Session.remove()
        get_users()
        return u'{0}: {1}'.format(nick, '\n{0}: '.format(nick).join(msgs))
