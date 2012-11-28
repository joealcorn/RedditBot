from RedditBot import bot, utils

from collections import OrderedDict
from copy import copy
import re


youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)',
              re.I)
youtube_re = re.compile(*youtube_re)

video_url = 'https://gdata.youtube.com/feeds/api/videos/{id}'
search_url = 'https://gdata.youtube.com/feeds/api/videos/'

api_params = {'v': 2, 'alt': 'jsonc'}


def get_video_information(vid_id, json=None):
    if json is None:
        r = utils.make_request(video_url.format(id=vid_id), params=api_params)
        if isinstance(r, str):
            return r
        else:
            if r.json.get('error'):
                return 'Error performing search ({0})'.format(r.json['error']['message'])

            data = r.json['data']
    else:
        data = json['data']['items'][0]

    length = OrderedDict()
    duration = data.get('duration', 0)

    if duration / 3600:
        # > 1 hour
        length['hours'] = '{0}h'.format(duration / 3600)
    if duration / 60:
        # > 1 minute
        length['minutes'] = '{0}m'.format(duration / 60 % 60)
    length['seconds'] = '{0}s'.format(duration % 60)

    information = {
        'title': data['title'],
        'length': ' '.join(x[1] for x in length.items()),
        'views': data.get('viewCount', 0),
        'author': data.get('uploader'),
        'nsfw': '[NSFW] - ' if data.get('contentRating', False) else ''
    }

    line = u"{nsfw}'{title}' - {length} - {views:,d} views - by {author}"
    return line.format(**information)


@bot.regex(youtube_re)
def youtube_url(context):
    vid_id = context.line['regex_search'].groups()[0]
    return get_video_information(vid_id)


@bot.command('y')
@bot.command
def youtube(context):
    '''Usage: .youtube <query>'''

    params = copy(api_params)
    params.update({
        'max-results': 1,
        'q': context.args
    })

    r = utils.make_request(search_url, params=params)

    if isinstance(r, str):
        return r
    elif 'error' in r.json:
        return 'Error performing search ({0})'.format(r.json['error']['message'])

    if r.json == 0:
        return 'No results found'

    vid_id = r.json['data']['items'][0]['id']

    return u'{info} - http://youtu.be/{id}'.format(
        info=get_video_information(vid_id, r.json),
        id=vid_id
    )
