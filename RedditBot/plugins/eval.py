from RedditBot import bot, utils

import sys
import __builtin__


@bot.command
def eval(context):
    '''.eval <command>'''
    if not utils.isadmin(context.line['prefix'], bot):
        return
    if context.args:
        try:
            bot.log(context, ('EVAL'), context.args)
            return str(__builtin__.eval(context.args))
        except:
            return repr(sys.exc_info()[1])
    else:
        return eval.__doc__
