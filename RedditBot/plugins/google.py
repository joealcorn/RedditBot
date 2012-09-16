from RedditBot import bot, utils

search_url = 'http://ajax.googleapis.com/ajax/services/search/web'


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
