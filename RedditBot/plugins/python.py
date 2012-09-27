
from RedditBot import bot
from RedditBot.pastebin import paste

import requests

url = 'http://eval.appspot.com/eval'

@bot.command
def python(context):
    '.python <exp>'

    try:
        r = requests.get(url, params={'statement': context.args})
    except Exception, e:
        return 'Failed to get the result from the server: {}.'.format(e)
    
    if not r.text or r.status_code != 200:
        return 'Failed to get the result from the server.'

    data = r.text.strip()
    
    if not data:
        return 'Empty result'
        
    lines = data.splitlines()
    
    if len(lines) > 1:
        p = paste(data, title='Executed by {}'.format(context.line['user']))
        if p['success']:
            return '{0}: {1}'.format(context.line['user'], p['url'])
        else:
            return lines[-1]
    
    return lines[0]
