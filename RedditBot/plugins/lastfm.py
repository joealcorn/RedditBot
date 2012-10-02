from RedditBot import bot, utils


url = 'http://ws.audioscrobbler.com/2.0/'


@bot.command
def lastfm(context):
    '''Usage: .lastfm <user 1> [<user 2>]'''
    args = [i for i in context.args.strip().split(' ') if i != '']
    if len(args) < 1:
        return lastfm.__doc__
    elif len(args) == 1:
        return last_played(args[0])
    elif len(args) <= 2:
        return compare(args[0], args[1])


def last_played(user):
    params = {
        'method': 'user.getrecenttracks',
        'user': user,
        'api_key': bot.config['LASTFM_API_KEY'],
        'format': 'json'
    }
    r = utils.make_request(url, params=params)
    if isinstance(r, str):
        return r
    elif 'error' in r.json:
        return r.json['message']

    r = r.json['recenttracks']

    info = {
        'artist': r['track'][0]['artist']['#text'],
        'user': r['@attr']['user'],
        'song': r['track'][0]['name'],
        'album': r['track'][0]['album']['#text']
    }

    line = u'{user} last played \'{song}\' from the album \'{album}\', by {artist}'
    return line.format(**info)


def compare(user1, user2):
    params = {
        'method': 'tasteometer.compare',
        'type1': 'user',
        'type2': 'user',
        'value1': user1,
        'value2': user2,
        'api_key': bot.config['LASTFM_API_KEY'],
        'format': 'json'
    }
    r = utils.make_request(url, params=params)
    if isinstance(r, str):
        return r
    elif 'error' in r.json:
        return r.json['message']

    r = r.json['comparison']
    info = {
        'user1': r['input']['user'][0]['name'],
        'user2': r['input']['user'][1]['name'],
        'percent': float(r['result']['score']),
    }

    line = u'{user1} vs {user2}: {percent:.0%} similarity'

    if 'artist' in r['result']['artists']:
        if int(r['result']['artists']['@attr']['matches']) < 2:
            artists = r['result']['artists']['artist']['name']
        else:
            artists = ', '.join([a['name'] for a in r['result']['artists']['artist']])

        line = line + u' - Common artists include {}'.format(artists)

    return line.format(**info)
