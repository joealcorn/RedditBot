from RedditBot import utils


def paste(contents, title=None, language='text', unlisted=0, password=None):
    paste = dict([(i, locals()[i]) for i in locals().keys() if locals()[i] is not None])
    url = 'http://buttscicl.es/paste/api/add'
    r = utils.make_request(url, params=paste, method='post', timeout=15)
    if isinstance(r, str):
        return {'success': False, 'error': r}
    else:
        return r.json
