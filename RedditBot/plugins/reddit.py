from RedditBot import bot, utils

import re

reddit_link = re.compile('http://(?:www\.)?redd(?:\.it/|it\.com/(?:tb|(?:r/[\w\.]+/)?comments)/)(\w+)(/.+/)?(\w{7})?')


@bot.command
def reddit(context):
    '''Usage: .reddit <subreddit>'''
    subreddit = context.args.strip().split(' ')[0]
    params = {}
    if subreddit is '':
        return 'Usage: .reddit <subreddit>'
    elif subreddit.lower().split('/')[0] in bot.config['REDDIT_BLACKLIST']:
        return 'No.'
    elif subreddit.lower().endswith(('/new', '/new/')):
        # reddit occasionally returns fuck all if the query string is not added
        params = {'sort': 'new'}

    url = 'http://www.reddit.com/r/{}.json'.format(subreddit)
    submission = utils.make_request(url, params)
    if isinstance(submission.json, dict):
        try:
            submission = submission.json['data']['children'][0]['data']
        except:
            return 'Could not fetch json, does that subreddit exist?'
    else:
        return submission

    info = {
        'username': context.line['user'],
        'subreddit': submission['subreddit'],
        'title': submission['title'],
        'up': submission['ups'],
        'down': submission['downs'],
        'shortlink': 'http://redd.it/' + submission['id']
    }
    line = u'{username}: /r/{subreddit} \'{title}\' +{up}/-{down} {shortlink}'.format(**info)
    return line


@bot.command
def karma(context):
    '''Usage: .karma <reddit_username>'''
    redditor = context.args.strip().split(' ')[0]
    if redditor is '':
        return 'Usage: .karma <redditor>'

    url = 'http://www.reddit.com/user/{}/about.json'.format(redditor)
    redditor = utils.make_request(url)
    if isinstance(redditor.json, dict):
        try:
            redditor = redditor.json['data']
        except:
            return 'Could not fetch json, does that user exist?'
    else:
        return redditor

    info = {
        'redditor': redditor['name'],
        'link': redditor['link_karma'],
        'comment': redditor['comment_karma'],
    }
    line = u'{redditor} has {link} link and {comment} comment karma'.format(**info)
    return line


@bot.regex(reddit_link)
def announce_reddit(context):
    submission_id = context.line['regex_search'].group(1)
    url = 'http://www.reddit.com/comments/{}.json'.format(submission_id)
    submission = utils.make_request(url)
    if isinstance(submission.json, list):
        try:
            submission = submission.json[0]['data']['children'][0]['data']
        except Exception:
            return 'Could not fetch json'
    else:
        return submission

    info = {
        'title': submission['title'],
        'up': submission['ups'],
        'down': submission['downs'],
        'shortlink': 'http://redd.it/' + submission['id']
    }
    line = u'\'{title}\' - +{up}/-{down} - {shortlink}'.format(**info)
    if context.line['regex_search'].group(3):
        # Link to comment
        return '[Comment] ' + line
    else:
        # Link to submission
        return line
