from RedditBot import bot, utils

import re

base_url = 'http://omdbapi.com'

info_line = "'{title}' ({yr}) - {rating}/10 - directed by {director} - {plot}"
search_line = "'{title}' ({yr}) - http://www.imdb.com/title/{id}/"

imdb_re = re.compile(
    r'https?://(?:www.)imdb.(com|co\.uk)/title/(?P<id>[A-Z0-9]+)/',
    re.I
)


@bot.regex(imdb_re)
def announce_title(context):
    media_id = context.line['regex_search'].group('id')
    r = utils.make_request(base_url, params={'i': media_id})
    if isinstance(r, str):
        return r

    # omdbapi returns Response as a string
    if r.json['Response'] in ('False', False):
        return 'Invalid media ID'

    info = {
        'title': r.json['Title'],
        'yr': r.json['Year'],
        'rating': r.json['imdbRating'],
        'director': r.json['Director'],
        'plot': r.json['Plot'][:60].strip() + '...'
    }

    return info_line.format(**info)


@bot.command('imdb')
def search(context):
    """Usage: .imdb <title>"""
    query = context.args

    r = utils.make_request(base_url, params={'s': query})
    if isinstance(r, str):
        return r

    # ombdapi returns Response = 'False' as a string
    # instead of bool, and only if the search fails
    if 'Response' in r.json:
        return r.json['Error']

    result = r.json['Search'][0]

    info = {
        'title': result['Title'],
        'id': result['imdbID'],
        'yr': result['Year']
    }

    return search_line.format(**info)
