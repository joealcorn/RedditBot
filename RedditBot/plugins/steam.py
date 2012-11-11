from RedditBot import bot, utils
from bs4 import BeautifulSoup


store_re = r'https?://store.steampowered.com/app/(?:\d{6})'
store_line = u'{title} on Steam - {price}'

title_attrs = {'class': 'apphub_AppName'}
price_attrs = {'itemprop': 'price'}


@bot.regex(store_re)
def store(context):
    url = context.line['regex_search'].string
    r = utils.make_request(url)
    if isinstance(r, str):
        return r

    soup = BeautifulSoup(r.content)
    info = {
        'title': soup.find('div', attrs=title_attrs).string,
        'price': soup.find('div', attrs=price_attrs).string.strip()
    }

    return store_line.format(**info)
