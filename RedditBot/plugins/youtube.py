# ported from kaa, which was ported from skybot

from RedditBot import bot

import re
import json
import time
import locale

import requests

youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)',
              re.I)
youtube_re = re.compile(*youtube_re)

base_url = 'http://gdata.youtube.com/feeds/api/'
url = base_url + 'videos/{0}?v=2&alt=jsonc'
search_api_url = base_url + 'videos?v=2&alt=jsonc&max-results=1'
video_url = "http://youtu.be/{0}"


def get_video_description(vid_id):
    r = requests.get(url.format(vid_id))
    data = json.loads(r.content)

    if data.get('error'):
        return

    data = data['data']
    data['title'] = data['title'].encode('utf-8', 'replace')

    out = '\'{title}\''.format(**data)

    if not data.get('duration'):
        return out

    out += ' - '
    length = data['duration']
    if length / 3600:  # > 1 hour
        out += '{0}h '.format(length / 3600)
    if length / 60:
        out += '{0}m '.format(length / 60 % 60)
    out += '{0}s'.format(length % 60)

    # The use of str.decode() prevents UnicodeDecodeError with some locales
    # See http://stackoverflow.com/questions/4082645/
    if 'viewCount' in data:
        out += ' - {0:,d} views'.format(data['viewCount'])

    out += ' - by {0}'.format(data['uploader'])

    if 'contentRating' in data:
        out = '[NSFW] - ' + out

    return out


@bot.regex(youtube_re)
def youtube_url(context):
    vid_id = context.line['regex_search'].groups()[0]
    return unicode(get_video_description(vid_id), 'utf8')


@bot.command('y')
@bot.command
def youtube(context):
    '.youtube <query>'

    r = requests.get(search_api_url, params=dict(q=context.args))

    data = json.loads(r.content)

    if 'error' in data:
        return 'error performing search'

    if data['data']['totalItems'] == 0:
        return 'no results found'

    vid_id = data['data']['items'][0]['id']

    return unicode(get_video_description(vid_id) + ' - ' + video_url.format(vid_id), 'utf8')
