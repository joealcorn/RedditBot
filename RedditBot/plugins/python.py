
from RedditBot import bot

import requests

url = 'http://eval.appspot.com/eval'

@bot.command('p')
@bot.command
def python(context):
    '.python <exp>'

    try:
        r = requests.get(url, params={'statement': context.args})
    except Exception, e:
        return 'Failed to get the result from the server: {}.'.format(e)
    
    if not r.text or r.status_code != 200:
        return 'Failed to get the result from the server.'
    
    if r.text.strip() == '':
        return 'Empty result'

    data = r.text

    if data.startswith('Traceback (most recent call last):'):
        data = data.splitlines()[-1]
    return data
