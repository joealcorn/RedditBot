class Config(object):
    # Server configuration
    SERVER = 'irc.gamesurge.net'
    PORT = 6667
    SSL = False
    TIMEOUT = 300
    NICK = 'RedditBot'
    REALNAME = 'https://github.com/buttscicles/RedditBot'
    CHANNELS = ['#RedditMC']

    ADMINS = ['*!*@AlcoJew.staff.reddit-minecraft',
              '*!joe@buttscicl.es',
              '*!edk141@edk141.co.uk',
              '*!*@edk141.staff.reddit-minecraft']

    # Plugin specific configs
    REDDIT_BLACKLIST = []
    TWITTER_BLACKLIST = []

    LASTFM_API_KEY = ''
    MCBOUNCER_KEY = ''
    WOLFRAMALPHA_KEY = ''
    GOOGLESEARCH_KEY = ''

    MINECRAFT_USER = ''
    MINECRAFT_PASSWORD = ''

    BITLY_KEY = ''
    BITLY_USER = ''
