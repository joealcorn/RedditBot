
from RedditBot import bot, utils

import re
import requests
import subprocess
import sys

api_url = 'https://api.github.com/{0}'

commit_re = re.compile(r'\bhttps?://github.com/(?P<owner>\w+)/(?P<repo>\w+)/commit/(?P<hash>[A-Fa-f0-9]+)/?(?![/\w])', re.I)
commit_request = 'repos/{owner}/{repo}/git/commits/{hash}'
commit_web = 'https://github.com/{owner}/{repo}/commit/{hash}'
commit_format = '\x02{short_url}\x02 -- {sha:.7} {author[name]} <{author[email]}>: {message}'
commit_format_pushedBy = '\x02{short_url}\x02 -- {sha:.7} {author[name]} <{author[email]}> (pushed by {committer[name]}): {message}'

commitlist_request = 'repos/{owner}/{repo}/commits'

gist_re = re.compile(r'\bhttps?://gist.github.com/(?P<id>[A-Fa-f0-9]+)\b')
gist_request = 'gists/{id}'
gist_format = '\x02{short_url}\x02 -- uploaded by {user[login]}, files: {file_list}, {comments} comments'

repo_re = re.compile(r'\bhttps?://github.com/(?P<owner>\w+)/(?P<repo>\w+)/?(?![/\w])', re.I)
repo_request = 'repos/{owner}/{repo}'
repo_format = '\x02{short_url}\x02 -- {name}: {description} ({owner[login]})'
repo_format_forkOf = '\x02{short_url}\x02 -- {name}: {description} ({owner[login]} forked from {parent[full_name]})'

thing_re = re.compile(r'^(?P<owner>\w+)/(?P<repo>\w+)(?:/(?:(?P<branch>\w+)|commit/(?P<hash>[A-Fa-f0-9]+)))?$', re.I)

gitio_url = 'http://git.io/'

redditbot_info = {
    'owner': 'buttscicles',
    'repo':  'RedditBot',
    'hash':  False
    }


try:
    redditbot_info['hash'] = subprocess.check_output('git log -1 --format=format:%H'.split(' ')).strip()
except:
    print 'Failed to get version hash: {}'.format(sys.exc_info())


def gitio_shorten(url):
    r = requests.post(gitio_url, data={'url': url})
    if r.status_code != 201:
        return False
    return r.headers['location']


def is_error(json):
    return type(json) is dict and (len(json.keys()) == 1 and 'message' in json)


def api_format_commit(info, verbose=False):
    request = commit_request.format(**info)
    r = utils.make_request(api_url.format(request))
    if isinstance(r, str) or is_error(r.json):
        return verbose and 'GitHub error: {}'.format(r.json['message']) if r.json else r
    commit = r.json
    commit['message'] = commit['message'].splitlines()[0].strip()
    commit['short_url'] = gitio_shorten(commit_web.format(**info))
    format = commit_format if commit['author']['email'] == commit['committer']['email'] else commit_format_pushedBy
    return format.format(**commit)


def api_format_branch(info, verbose=False):
    request = commitlist_request.format(**info)
    r = utils.make_request(api_url.format(request), params={'sha': info['branch']})
    if isinstance(r, str) or is_error(r.json):
        return verbose and 'GitHub error: {}'.format(r.json['message']) if r.json else r
    commit = r.json[0]['commit']
    commit['sha'] = r.json[0]['sha']
    info['hash'] = commit['sha']
    commit['message'] = commit['message'].splitlines()[0].strip()
    commit['short_url'] = gitio_shorten(commit_web.format(**info))
    format = commit_format if commit['author']['email'] == commit['committer']['email'] else commit_format_pushedBy
    return format.format(**commit)


def api_format_gist(info, verbose=False):
    request = gist_request.format(**info)
    r = utils.make_request(api_url.format(request))
    if isinstance(r, str) or is_error(r.json):
        return verbose and 'GitHub error: {}'.format(r.json['message']) if r.json else r
    gist = r.json
    gist['file_list'] = ' '.join(gist['files'].keys())
    gist['short_url'] = gitio_shorten(gist['html_url'])
    return gist_format.format(**gist)


def api_format_repo(info, verbose=False):
    request = repo_request.format(**info)
    r = utils.make_request(api_url.format(request))
    if isinstance(r, str) or is_error(r.json):
        return verbose and 'GitHub error: {}'.format(r.json['message']) if r.json else r
    repo = r.json
    repo['description'] = repo['description'].strip()
    repo['short_url'] = gitio_shorten(repo['html_url'])
    format = repo_format_forkOf if repo['fork'] else repo_format
    return format.format(**repo) 


@bot.regex(commit_re)
def announce_commit(context):
    return api_format_commit(context.line['regex_search'].groupdict()) or None


@bot.command('github')
def get_github(context):
    '''.github <owner>/<repo>[/<branch>|/commit/<hash>]'''
    m = thing_re.match(context.args)
    if not m:
        return get_github.__doc__
    if m.group('hash'):
        return api_format_commit(m.groupdict(), verbose=True)
    elif m.group('branch'):
        return api_format_branch(m.groupdict(), verbose=True)
    else:
        return api_format_repo(m.groupdict(), verbose=True)


@bot.regex(gist_re)
def announce_gist(context):
    return api_format_gist(context.line['regex_search'].groupdict()) or None


@bot.command('gist')
def get_gist(context):
    '''.gist <id>'''
    if not re.match('^[A-Fa-f0-9]+$', context.args):
        return get_gist.__doc__
    return api_format_gist({'id': context.args}, verbose=True) or 'Failed, check gist ID'


@bot.regex(repo_re)
def announce_repo(context):
    return api_format_repo(context.line['regex_search'].groupdict()) or None


@bot.command('version')
def announce_bot():
    if not redditbot_info['hash']:
        return 'Unknown.'
    try:
        info_str = api_format_commit(redditbot_info, verbose=True)
    except:
        info_str = False
    return 'I am at {}'.format(info_str) if info_str else 'Unable to retrieve information from GitHub, probably running on a private branch.'
