
import urllib2, urllib, json

def paste(data, user="Anonymous", lang="text", private="true", password=None):
    data = {
        'paste_user': user,
        'paste_data': data,
        'paste_lang': lang,
        'api_submit': 'true',
        'mode': 'json',
        'paste_private': private
    }

    if password:
        data['paste_password'] = password

    req = urllib2.urlopen("http://paste.thezomg.com", urllib.urlencode(data))
    data = req.read()

    if data:
        data = json.loads(data)
        id = data['result']['id']
        hash = data['result']['hash']

        return "http://paste.thezomg.com/%s/%s/" % (id, hash)
