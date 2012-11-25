from RedditBot import bot, utils

import re

tweet_re = re.compile('https?://(?:www.)?twitter.com/.+/status/([0-9]{18})')
status_url = 'https://api.twitter.com/1/statuses/show/{}.json'
latest_url = 'http://api.twitter.com/1/statuses/user_timeline.json'
line = u'@{screen_name}: {tweet}'


@bot.regex(tweet_re)
def announce_tweet(context):
    ''' Announces tweets as they are posted in the channel '''
    tweet_id = context.line['regex_search'].group(1)
    url = status_url.format(tweet_id)
    response = utils.make_request(url, params={'include_entities': 1})
    if isinstance(response, str):
        return response

    tweet = response.json['text']

    if 'entities' in response.json:
        if 'urls' in response.json['entities']:
            for url in response.json['entities']['urls']:
                replacement = url['expanded_url']
                if len(replacement) <= int(bot.config['TWITTER_UNSHORTEN_LIMIT']) or 0:
                    tweet = tweet.replace(url['url'], replacement)

    info = {
        'screen_name': response.json['user']['screen_name'],
        'tweet': tweet
    }
    if info['screen_name'].lower() in bot.config['TWITTER_BLACKLIST']:
        return
    return utils.unescape_html(line.format(**info))


@bot.command
def twitter(context):
    '''Usage: .twitter <username>'''
    username = context.args.strip().split(' ')[0]
    if username is '':
        return 'Usage: .twitter <username>'
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

    tweet = response.json[0]['text']

    if 'entities' in response.json[0]:
        if 'urls' in response.json[0]['entities']:
            for url in response.json[0]['entities']['urls']:
                replacement = url['expanded_url']
                if len(replacement) <= int(bot.config['TWITTER_UNSHORTEN_LIMIT']) or 0:
                    tweet = tweet.replace(url['url'], replacement)

    info = {
        'screen_name': response.json[0]['user']['screen_name'],
        'tweet': tweet
    }
    return utils.unescape_html(line.format(**info))
