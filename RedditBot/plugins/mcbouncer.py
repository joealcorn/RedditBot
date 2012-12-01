
from RedditBot import bot, utils


def mcb_status():
    if not bot.config.get('MCBOUNCER_KEY', False):
        return {'success': False, 'message': "MCBouncer not configured"}
    url = "http://mcbouncer.com/api/getBanCount/%s/AlcoJew" % bot.config["MCBOUNCER_KEY"]
    r = utils.make_request(url)
    if r:
        if type(r) is str:
            return {'success': False, 'message': r}
        if r.status_code == 200:
            if r.json:
                return {'success': True, 'message': "MCBouncer API operational"}
            else:
                return {'success': False, 'message': "MCBouncer Error - malformed data"}
        else:
            return {'success': False, 'message': "MCBouncer Error - server error"}
    else:
        return {'success': False, 'message': "MCBouncer Error - no data returned"}


@bot.command('mcb')
@bot.command
@utils.cooldown(bot)
def mcbouncer(context):
    '''Usage: .mcb'''
    return mcb_status()['message']
