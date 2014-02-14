from RedditBot import bot, utils

import re
import json
import oauth2 as oauth

tweet_re = re.compile('https?://(?:www\.|mobile\.)?twitter.com/.+/status(?:es)?/([0-9]{18})')
status_url = 'https://api.twitter.com/1.1/statuses/show/{}.json'
latest_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
line = u'@{screen_name}: {tweet}'


class Tweet(object):

    _consumer = oauth.Consumer(
        key=bot.config['TWITTER_CONSUMER_KEY'],
        secret=bot.config['TWITTER_CONSUMER_SECRET']
    )
    _token = oauth.Token(
        key=bot.config['TWITTER_ACCESS_KEY'],
        secret=bot.config['TWITTER_ACCESS_SECRET']
    )
    client = oauth.Client(_consumer, _token)

    @classmethod
    def make_request(self, url, params=None):
        if params is not None:
            # As far as I can tell oauth2.client doesn't support
            # adding arbritrary params to the url like requests,
            # so we do it manually
            query_string = '&'.join(k + '=' + str(v) for k, v in params.items())
            url = '{0}?{1}'.format(url, query_string)

        try:
            resp, body = self.client.request(url, 'GET')
        except Exception:
            return None
        else:
            return json.loads(body), int(resp['status'])

    @classmethod
    def by_id(self, id):
        url = status_url.format(id)
        return self.make_request(url, {'include_entities': 1})

    @classmethod
    def latest(self, username):
        params = {
            'screen_name': username,
            'count': 1,
            'include_entities': 1
        }
        return self.make_request(latest_url, params)


def extract_info(json):
    info = {
        'screen_name': json['user']['screen_name'],
        'tweet': json['text'].replace('\n', ' ')
    }

    if 'entities' in json:
        if 'urls' in json['entities']:
            for url in json['entities']['urls']:
                replacement = url['expanded_url']
                if len(replacement) <= int(bot.config['TWITTER_UNSHORTEN_LIMIT']) or 0:
                    info['tweet'] = info['tweet'].replace(url['url'], replacement)

        if 'media' in json['entities']:
            for thing in json['entities']['media']:
                if thing['type'] == 'photo':
                    img_url = 'http://' + thing['display_url']
                    if len(img_url) <= int(bot.config['TWITTER_UNSHORTEN_LIMIT']):
                        info['tweet'] = info['tweet'].replace(thing['url'], img_url)

    return info


@bot.regex(tweet_re)
def announce_tweet(context):
    ''' Announces tweets as they are posted in the channel '''
    tweet_id = context.line['regex_search'].group(1)
    tweet, code = Tweet.by_id(tweet_id)

    if not tweet:
        # Exception, fail silently so as not to spam the channel
        return
    elif code != 200:
        return 'Something went wrong ({0})'.format(code)

    tweet = extract_info(tweet)
    if tweet['screen_name'].lower() in bot.config['TWITTER_BLACKLIST']:
        return

    return utils.unescape_html(line.format(**tweet))


@bot.command
def twitter(context):
    '''Usage: .twitter <username>'''
    username = context.args.strip().split(' ')[0]
    if username in ('', None):
        return twitter.__doc__
    elif username.lower().lstrip('@') in bot.config['TWITTER_BLACKLIST']:
        return 'No.'

    tweet, code = Tweet.latest(username)
    if tweet is None:
        # Exception occcured
        return
    elif code == 404:
        return "{0}: That user hasn't tweeted yet".format(context.line['user'])
    elif code != 200:
        return 'Something went wrong ({0})'.format(code)

    tweet = extract_info(tweet[0])
    return utils.unescape_html(line.format(**tweet))
