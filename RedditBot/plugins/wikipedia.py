# ported from skybot

from RedditBot import bot

import xml.etree.ElementTree as etree
from urllib import quote, unquote
import re

import requests

search_url = 'http://en.wikipedia.org/w/api.php'
search_params = {
    'action': 'opensearch',
    'format': 'xml'
}

paren_re = re.compile('\s*\(.*\)$')

wiki_re = re.compile('(\http|\https)(\://*.[a-zA-Z]{0,1}\.*wikipedia.+?)'
                     '(\com/wiki/|\org/wiki/)(?!File\:|Template\:)([^\s]+)')


def wiki_search(query):
    result = {
        'description': None,
        'url': None
    }

    search_params.update({'search': unquote(query)})
    r = requests.get(search_url, params=search_params)
    data = etree.fromstring(r.content)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = data.findall(ns + 'Section/' + ns + 'Item')

    if items == []:
        if data.find('error') is not None:
            result['description'] = 'Error: {code}: {info}'.format(data.find('error').attrib)
        else:
            result['description'] = 'No results found'
        return result

    def extract(item):
        return [item.find(ns + e).text for e in ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = '\x02' + paren_re.sub('', title) + '\x02 -- '

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = re.sub('\s+', ' ', desc).strip()  # remove excess spaces

    if len(desc) > 300:
        desc = desc[:300].rsplit(' ', 1)[0] + '...'

    result.update({
        'description': desc,
        'url': quote(url, ':/')
    })

    return result


@bot.regex(wiki_re)
def wiki_find(context):
    query = context.line['regex_search'].groups()[-1]
    result = wiki_search(query)
    print result
    if result['url'] is None:
        return None
    else:
        return result['description']


@bot.command('wp')
@bot.command
def wikipedia(context):
    '''.wikipedia <query>'''
    result = wiki_search(context.args)
    if result['url'] is None:
        return u'{0}'.format(result['description'])
    else:
        return u'{0} -- {1}'.format(result['description'], result['url'])
