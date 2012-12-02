from RedditBot.ircglob import glob

from itertools import imap, ifilter
from HTMLParser import HTMLParser
from functools import wraps
from time import time
import random

import requests

headers = {'User-Agent': 'irc.gamesurge.net #redditmc/RedditBot'}
timeout = 5


def newlines(ar):
    return imap(lambda x: x + '\n', ar)


def stripnewlines(ar):
    return list(imap(lambda x: x.rstrip('\n'), ifilter(lambda x: x != '\n', ar)))


def isadmin(prefix, bot):
    admins = bot.config.get('ADMINS', [])
    return any(imap(lambda x: glob(x).matches(prefix), admins))


def isignored(prefix, bot):
    ignore = bot.config.get('IGNORE', [])
    return any(imap(lambda x: glob(x).matches(prefix), ignore))


def make_request(url, params={}, method='get', timeout=timeout):
    try:
        if method.lower() == 'post':
            r = requests.post(url, data=params, headers=headers, timeout=timeout)
        elif method.lower() == 'get':
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
        else:
            raise Exception('Unsupported HTTP Method')
    except requests.exceptions.ConnectionError:
        return 'Connection error'
    except requests.exceptions.Timeout:
        return 'Request timed out ({} secs)'.format(timeout)
    except requests.exceptions.HTTPError:
        return 'HTTP Error'
    except requests.exceptions.TooManyRedirects:
        return 'Too many redirects'

    return r


def shorten_url(bot, url):
    if not 'BITLY_KEY' in bot.config or not 'BITLY_USER' in bot.config:
        return None
    par = {
        'format':  'json',
        'domain':  'j.mp',
        'login':   bot.config['BITLY_USER'],
        'apiKey':  bot.config['BITLY_KEY'],
        'longUrl': url
        }
    r = make_request('http://api.bitly.com/v3/shorten', params=par)
    if isinstance(r, str): return None
    if r.status_code == 200:
        return r.json['data']['url']


def unescape_html(string):
    return HTMLParser().unescape(string)


def cooldown(bot):
    '''
    Prevents commands being used multiple times in a certain time period
    Set module.function.cooldown to an int to set the cooldown period

    '''
    def decoration(func):
        @wraps(func)
        def wrapper(context):

            cfg = '{0}.{1}.cooldown'.format(func.__module__, func.__name__).lower()
            ts = '{0}.{1}.timestamp'.format(func.__module__, func.__name__).lower()
            ct = int(time())

            # func.__module__ changes after reloading, work around that
            if cfg.startswith('redditbot.plugins'):
                cfg = cfg[18:]
            if ts.startswith('redditbot.plugins'):
                ts = ts[18:]

            if ts in bot.data and cfg in bot.config and not isadmin(context.line['prefix'], bot):
                last_used = ct - bot.data[ts]
                period = int(bot.config[cfg])

                if last_used < period:
                    bot.reply('That has been already been used within the last {0} seconds'.format(period),
                              context.line, False, True, context.line['user'], nofilter=True)
                    return

            bot.data[ts] = ct

            return func(context)
        return wrapper

    return decoration


def require_admin(bot, message='That command can only be run by admins', notice=True):
    '''
    Decorator for commands that can only be run by an admin

    '''
    def decoration(func):
        @wraps(func)
        def wrapper(context):
            if not isadmin(context.line['prefix'], bot):
                if notice:
                    bot.reply(message, context.line, False, True, context.line['user'], nofilter=True)
                    return
                else:
                    return message

            else:
                return func(context)
        return wrapper
    return decoration


### begin insult code, shamelessly stolen from rbot

adj = [
"acidic", "antique", "contemptible",
"culturally-unsound", "despicable",
"evil", "fermented", "festering",
"foul", "fulminating", "humid",
"impure", "inept", "inferior",
"industrial", "left-over",
"low-quality", "malodorous",
"off-color", "penguin-molesting",
"petrified", "pointy-nosed", "salty",
"sausage-snorfling", "tastless",
"tempestuous", "tepid", "tofu-nibbling",
"unintelligent", "unoriginal", "uninspiring",
"weasel-smelling", "wretched",
"spam-sucking", "egg-sucking",
"decayed", "halfbaked", "infected",
"squishy", "porous", "pickled",
"coughed-up", "thick", "vapid",
"hacked-up", "unmuzzled", "bawdy",
"vain", "lumpish", "churlish",
"fobbing", "rank", "craven",
"puking", "jarring", "fly-bitten",
"pox-marked", "fen-sucked",
"spongy", "droning", "gleeking",
"warped", "currish", "milk-livered",
"surly", "mammering", "ill-borne",
"beef-witted", "tickle-brained",
"half-faced", "headless",
"wayward", "rump-fed", "onion-eyed",
"beslubbering", "villainous",
"lewd-minded", "cockered", "full-gorged",
"rude-snouted", "crook-pated",
"pribbling", "dread-bolted", "fool-born",
"puny", "fawning", "sheep-biting",
"dankish", "goatish", "weather-bitten",
"knotty-pated", "malt-wormy",
"saucyspleened", "motley-mind",
"it-fowling", "vassal-willed", "loggerheaded",
"clapper-clawed", "frothy",
"ruttish", "clouted",
"common-kissing", "pignutted",
"folly-fallen", "plume-plucked",
"flap-mouthed", "swag-bellied",
"dizzy-eyed", "gorbellied", "weedy",
"reeky", "measled", "spur-galled",
"mangled", "impertinent", "bootless",
"toad-spotted", "hasty-witted",
"horn-beat", "yeasty", "boil-brained",
"tottering", "hedge-born", "hugger-muggered",
"elf-skinned"
]

amt = [
"accumulation", "bucket", "coagulation",
"enema-bucketful", "gob", "half-mouthful",
"heap", "mass", "mound", "petrification",
"pile", "puddle", "stack", "thimbleful",
"tongueful", "ooze", "quart", "bag",
"plate", "ass-full", "assload"
]

noun = [
"bat toenails", "bug spit", "cat hair",
"chicken piss", "dog vomit", "dung",
"fat-woman's stomach-bile", "fish heads",
"guano", "gunk", "pond scum", "rat retch",
"red dye number-9", "Sun IPC manuals",
"waffle-house grits", "yoo-hoo", "dog balls",
"seagull puke", "cat bladders", "pus",
"urine samples", "squirrel guts", "snake assholes",
"snake bait", "buzzard gizzards", "cat-hair-balls",
"rat-farts", "pods", "armadillo snouts",
"entrails", "snake snot", "eel ooze",
"slurpee-backwash", "toxic waste", "Stimpy-drool",
"poopy", "poop", "craptacular carpet droppings",
"jizzum", "cold sores", "anal warts"
]


def generate_insult():
    adj1 = random.choice(adj)
    adj2 = adj1
    while adj2 == adj1:
        adj2 = random.choice(adj)

    amt1 = random.choice(amt)
    noun1 = random.choice(noun)
    return '{0} {1} of {2} {3}'.format(adj1, amt1, adj2, noun1)
