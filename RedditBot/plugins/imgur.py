
from RedditBot import bot, utils

import re
import requests

image_re_1 = re.compile(r'https?://i.imgur.com/(?P<hash>\w+)\.(?:gif|jpg|jpeg|png)/?(?![/\w])', re.I)
image_re_2 = re.compile(r'https?://imgur.com/(?P<hash>\w+)/?(?![/\w])', re.I)
image_url = 'http://api.imgur.com/2/image/{hash}.json'
image_format = '{0}: {link} -- {human_type} -- {views} views -- {title}'

album_re = re.compile(r'https?://imgur.com/a/(?P<id>\w+)/?(?![/\w])', re.I)
album_url = 'http://api.imgur.com/2/album/{id}.json'
album_format = '{0}: {n_images} images -- {title}'

static_types = {
    'image/png':  'PNG',
    'image/jpeg': 'JPEG'
    }

def image_type(image):
    if image['type'] in static_types:
        return static_types[image['type']]
    if image['type'] == 'image/gif':
        return 'Animated GIF' if image['animated'] == 'true' else 'Static GIF'
    return image['type']

@bot.regex(image_re_1)
@bot.regex(image_re_2)
def announce_image(context):
    request = image_url.format(**context.line['regex_search'].groupdict())
    r = requests.get(request)
    print request
    #if isinstance(r, str):
    #    return r
    print r.text
    image = r.json['image']['image']
    print repr(image)
    image['human_type'] = image_type(image)
    image['title'] = image['title'] or 'no title'
    image['link'] = r.json['image']['links']['original']
    return image_format.format(context.line['user'], **image)
