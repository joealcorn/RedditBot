from RedditBot import bot, utils
import re
from datetime import timedelta


video_link = re.compile('http://(?:www.)?vimeo.com/(?P<id>\d{8})')
video_url = 'http://vimeo.com/api/v2/video/{id}.json'
video_line = u"'{title}' - {length} - {views:,d} views - by {author}"


@bot.regex(video_link)
def video(context):
    video_id = context.line['regex_search'].groups()[0]
    url = video_url.format(id=video_id)
    r = utils.make_request(url)
    if isinstance(r, str):
        return r

    info = {
        'title': r.json[0]['title'],
        'length': timedelta(seconds=r.json[0]['duration']),
        'views': r.json[0]['stats_number_of_plays'],
        'author': r.json[0]['user_name']
    }

    return video_line.format(**info)
