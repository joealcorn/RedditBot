# ported from skybot

from RedditBot import bot

from urllib import quote

import xml.etree.ElementTree as etree

import re

import requests

api_prefix = 'http://en.wikipedia.org/w/api.php'
search_url = api_prefix + '?action=opensearch&format=xml'

paren_re = re.compile('\s*\(.*\)$')

wiki_re = re.compile('(\http|\https)(\://*.[a-zA-Z]{0,1}\.*wikipedia.+?)'
                     '(\com/wiki/|\org/wiki/)(?!File\:)([^\s]+)')


def wiki_search(query):
    r = requests.get(search_url, params=dict(search=query))
    data = etree.fromstring(r.content)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = data.findall(ns + 'Section/' + ns + 'Item')

    if items == []:
        if data.find('error') is not None:
            return 'error: {code}: {info}'.format(data.find('error').attrib)
        else:
            return 'no results found'

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
    
    return desc, url


@bot.regex(wiki_re)
def wiki_find(context):
    query = context.line['regex_search'].groups()[-1]
    desc, _ = wiki_search(query)
    return desc


@bot.command('wp')
@bot.command
def wikipedia(context):
    '''.wikipedia <query>'''
    desc, url = wiki_search(context.args)
    return u'{0} -- {1}'.format(desc, quote(url, ':/'))
