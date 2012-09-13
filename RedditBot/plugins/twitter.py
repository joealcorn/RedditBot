from RedditBot import bot, utils

import re

tweet_re = re.compile('https?://(www.)?twitter.com/.+/status/([0-9]{18})')
status_url = 'https://api.twitter.com/1/statuses/show/{}.json'
latest_url = 'http://api.twitter.com/1/statuses/user_timeline.json'
line = u'@{screen_name}: {tweet}'


@bot.regex(tweet_re)
def announce_tweet(context):
    ''' Announces tweets as they are posted in the channel '''
    tweet_id = context.line['regex_search'].group(2)
    url = status_url.format(tweet_id)
    response = utils.make_request_json(url)
    if not isinstance(response, dict):
        return response

    info = {'screen_name': response['user']['screen_name'],
            'tweet': response['text']}
    return utils.unescape_html(line.format(**info))


@bot.command
def twitter(context):
    ''' Gets the latest tweet for a username '''
    username = context.args.strip().split(' ')[0]
    if username is '':
        return 'Usage: .twitter <username>'

    params = {'screen_name': username, 'count': 1}
    response = utils.make_request_json(latest_url, params)
    if not isinstance(response, list):
        return response
    elif response == []:
        return 'No results found for that name'

    info = {'screen_name': response[0]['user']['screen_name'],
            'tweet': response[0]['text']}
    return utils.unescape_html(line.format(**info))
