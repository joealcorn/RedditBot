from RedditBot import bot

from random import seed, randint

@bot.regex('^!squatlylist')
def squatlylist(context):
    return 'squatly list: squatly'


high = 0
target = 0


def reset():
    global target
    seed()
    target = randint(3, 5)

@bot.regex('.*')
def counting(context):
    global high
    try:
        next = int(context.args)
        if next == 1:
            reset()
            high = 0
        if next != high + 1:
            high = 0
        else:
            high = next
            if next + 1 == target:
                high += 1
                return str(high)
    except ValueError:
        high = 0
