
from RedditBot import bot, utils

import BeautifulSoup
import re

url = 'http://www39.wolframalpha.com/input/'

letters_re = re.compile(r'^(?:\w \| )+\w$')

@bot.command('wa')
@bot.command
def wolframalpha(context):
    if not context.args:
        return wolframalpha.__doc__
    
    result = utils.make_request(url, params={'asynchronous': 'false', 'i': context.args}, timeout=10)
    if type(result) is str:
        return result
    
    try:
        html = result.text
        tree = BeautifulSoup.BeautifulSoup(html)
    except Exception:
        return 'Error decoding WolframAlpha response.'
    
    html = tree.prettify().decode('utf8')
    
    if re.search('sure what to do with your input', html):
            return 'No results.'
    
    found = re.findall('"stringified":\s"([^"]+)"', html)
    
    if not found: 
        return 'Couldn\'t find results, bug Steve for a proper API.'
    
    results = found[:2][-1].split('\\n')
    
    def format_result_nicely(result):
        if letters_re.match(result):
            return result.replace(' | ', '')
        return result
    
    results = [format_result_nicely(r) for r in results]
    
    return ', '.join(results)
