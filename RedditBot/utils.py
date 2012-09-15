
from RedditBot.ircglob import glob
from itertools import imap, ifilter
from HTMLParser import HTMLParser
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


def make_request(url, params={}):
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return 'Connection error'
    except requests.exceptions.Timeout:
        return 'Request timed out ({} secs)'.format(timeout)
    except requests.exceptions.HTTPError:
        return 'HTTP Error'
    except requests.exceptions.TooManyRedirects:
        return 'Too many redirects'
    except:
        return 'Unhandled exception'
    return r


def unescape_html(string):
    return HTMLParser().unescape(string)
