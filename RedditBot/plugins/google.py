from RedditBot import bot, utils

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

search_url = 'http://ajax.googleapis.com/ajax/services/search/web'

cse_url = 'https://www.googleapis.com/customsearch/v1'
cse_result = '{link} -- {title}'
cse_result_more_results = ' -- more result{s} at {link}'
cse_result_n_more_results = ' -- {n} more result{s} at {link}'

cse = {
    'xkcd':         '012652707207066138651:zudjtuwe28q'
    }


def google_cse(query, cx, key=None):
    if not key:
        if 'GOOGLESEARCH_KEY' in bot.config: key = bot.config['GOOGLESEARCH_KEY']
        else: return {'success': False, 'error': 'Google Custom Search key not configured'}
    r = utils.make_request(cse_url, params={'key': key, 'cx': cx, 'q': query})
    if isinstance(r, str):
        return {'success': False, 'error': r}
    return r.json


def wrap_cse(cx, name=None):
    def wrapped(context):
        r = google_cse(context.args, cx)
        if r.get('success', True):
            if 'items' in r:
                output = cse_result.format(**r['items'][0])
                n = int(r['queries']['request'][0]['totalResults']) - 1
                if n > 0:
                    long_url = 'https://www.google.com/cse?{0}'.format(urlencode({'cx': cx, 'q': context.args}))
                    short_url = utils.shorten_url(bot, long_url)
                    if short_url:
                        s = '' if n == 1 else 's'
                        format = cse_result_more_results if n > 10 else cse_result_n_more_results
                        output += format.format(s=s, n=n, link=short_url)
                return output
            else:
                return 'No results.'
        else:
            return 'Error: {0}'.format(r['error'])
    if name:
        wrapped.__doc__ = '.{0} <query>'.format(name)
    return wrapped


def add_cse_command(name, command=None):
    command = command or name
    bot.command(name)(wrap_cse(cse[name], name=name))


map(add_cse_command, cse.keys())


@bot.command('g')
@bot.command
def google(context):
    '''.g <query>'''
    query = context.args
    r = utils.make_request(search_url, params={'v': '1.0', 'safe': 'off', 'q': query})

    if not r.json['responseData']['results']:
        return 'no results found'

    first_result = r.json['responseData']['results'][0]
    title = utils.unescape_html(first_result['titleNoFormatting'])
    ret = title + ' - ' + first_result['unescapedUrl']

    return u'{0}: {1}'.format(context.line['user'], ret)

