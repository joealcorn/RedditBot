from RedditBot import bot

from random import seed, randint

@bot.regex('^!squatlylist')
def squatlylist(context):
    return 'squatly list: squatly'


high = 0
target = 0

seed()

def reset():
    global target
    target = randint(2, 4)

@bot.regex('.*')
def counting(context):
    global high
    try:
        next = int(context.args)
        if next == 1:
            print 'a'
            reset()
            high = 0
        if next != high + 1:
            print 'b'
            high = 0
        else:
            print 'c'
            high = next
            if next + 1 == target:
                print 'd'
                high += 1
                return str(high)
    except ValueError:
        high = 0
