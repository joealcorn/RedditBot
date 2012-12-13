from RedditBot import bot, utils
from bs4 import BeautifulSoup


store_re = r'.*(https?://store.steampowered.com/app/(?:\d+))'
store_line = u'{title} on Steam - {price}'

title_attrs = {'class': 'apphub_AppName'}
price_attrs = {'itemprop': 'price'}

agecheck_params = {
    'snr': '1_agecheck_agecheck__age-gate',
    'ageDay': '1',
    'ageMonth': 'January',
    'ageYear': '1970'
}


@bot.regex(store_re)
def store(context):
    url = context.line['regex_search'].group(1)
    r = utils.make_request(url)
    if isinstance(r, str):
        return r
    elif len(r.history) > 0:
        if 'agecheck' not in r.url:
            # App doesn't exist
            return

        # Steam wants us to confirm our age
        r = utils.make_request(r.url, params=agecheck_params, method='POST')
        if isinstance(r, str):
            return r

    soup = BeautifulSoup(r.content.decode('utf8', errors='replace'))
    info = {
        'title': soup.find('div', attrs=title_attrs).string,
        'price': soup.find('div', attrs=price_attrs).string.strip()
    }

    return store_line.format(**info)
