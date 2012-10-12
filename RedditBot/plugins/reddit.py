from RedditBot import bot, utils

import re
import requests

reddit_link = re.compile('http://(?:www\.)?redd(?:\.it/|it\.com/(?:tb|(?:r/[\w\.]+/)?comments)/)(\w+)(/.+/)?(\w{7})?')

any_link_re = re.compile(r'\bhttps?://(?:[\w_]+\.)+[\w_]+(?:/(?:[^ ]*[^.])?)?\b', re.I)


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
    if isinstance(submission, str):
        return submission
    else:
        try:
            submission = submission.json['data']['children'][0]['data']
        except:
            return 'Could not fetch json, does that subreddit exist?'

    info = {
        'username': context.line['user'],
        'subreddit': submission['subreddit'],
        'title': utils.unescape_html(submission['title'].replace('\n', '')),
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
    if isinstance(redditor, str):
        return redditor
    else:
        try:
            redditor = redditor.json['data']
        except:
            return 'Could not fetch json, does that user exist?'

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
    if isinstance(submission, str):
        return submission
    else:
        try:
            submission = submission.json[0]['data']['children'][0]['data']
        except Exception:
            return 'Could not fetch json'

    info = {
        'title': utils.unescape_html(submission['title'].replace('\n', '')),
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


last_link = None
@bot.regex(any_link_re)
def link(context):
    global last_link
    last_link = context.line['regex_search'].group(0)


@bot.command('source')
def reddit_source(context):
    if not context.args:
        context.args = last_link
    if not context.args:
        return
    urls = [context.args]
    imgur = re.match(r'\bhttp://i\.imgur\.com/(?P<hash>\w+)\.\b', context.args)
    if imgur:
        print 'imgur link: {hash}'.format(**imgur.groupdict())
        urls.append('http://imgur.com/{hash}'.format(**imgur.groupdict()))
    posts = []
    try:
        for u in urls:
            r = requests.get('http://www.reddit.com/api/info.json', params={'url': u})
            posts.extend(r.json['data']['children'])
        if not posts:
            return 'Link is not on reddit'
    except:
        return 'Couldn\'t get link data from reddit'
    posts.sort(key=lambda x: x['data']['created'])
    return '/r/{subreddit} -- http://redd.it/{id}'.format(**posts[0]['data'])
