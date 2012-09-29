
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
