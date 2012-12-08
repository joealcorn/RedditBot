from RedditBot import bot, utils

import re

tweet_re = re.compile('https?://(?:www\.|mobile\.)?twitter.com/.+/status(?:es)?/([0-9]{18})')
status_url = 'https://api.twitter.com/1/statuses/show/{}.json'
latest_url = 'http://api.twitter.com/1/statuses/user_timeline.json'
line = u'@{screen_name}: {tweet}'


def extract_info(json):
    info = {
        'screen_name': json['user']['screen_name'],
        'tweet': json['text']
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
    url = status_url.format(tweet_id)
    response = utils.make_request(url, params={'include_entities': 1})
    if isinstance(response, str):
        return response

    tweet = extract_info(response.json)

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

    params = {
        'screen_name': username,
        'count': 1,
        'include_entities': 1
    }

    response = utils.make_request(latest_url, params)
    if isinstance(response, str):
        return response
    elif response.status_code == 404:
        return 'Nonexistent user'
    elif response.json == []:
        return 'That user hasn\'t tweeted yet'

    tweet = extract_info(response.json[0])

    return utils.unescape_html(line.format(**tweet))
