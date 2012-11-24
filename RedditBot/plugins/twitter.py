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
    response = utils.make_request(url)
    if not isinstance(response.json, dict):
        return response

    info = {'screen_name': response.json['user']['screen_name'],
            'tweet': response.json['text']}
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

    params = {'screen_name': username, 'count': 1}
    response = utils.make_request(latest_url, params)
    if isinstance(response, str):
        return response
    elif response.status_code == 404:
        return 'Nonexistent user'
    elif response.json == []:
        return 'That user hasn\'t tweeted yet'

    info = {'screen_name': response.json[0]['user']['screen_name'],
            'tweet': response.json[0]['text']}
    return utils.unescape_html(line.format(**info))
