class Config(object):
    # Server configuration
    SERVER = 'irc.gamesurge.net'
    PORT = 6667
    SSL = False
    TIMEOUT = 300
    NICK = 'RedditBot'
    REALNAME = 'https://github.com/buttscicles/RedditBot'
    CHANNELS = ['#RedditMC', '#countdown']

    ADMINS = ['*!*@AlcoJew.staff.reddit-minecraft',
              '*!joe@buttscicl.es',
              '*!edk141@edk141.co.uk',
              '*!*@edk141.staff.reddit-minecraft']
    
    REJOIN_KICKERS = ['SpamServ']

    # Plugin specific configs

    # This needs to a valid SQLAlchemy connection string
    # Find one for your preferred db + driver here:
    # http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html
    TELL_DB = 'sqlite:///{0}.{1}.db'.format(NICK, SERVER)

    REDDIT_BLACKLIST = []
    TWITTER_BLACKLIST = []
    COUNTDOWN_CHANNELS = ['#countdown']
    SNOOP_CHANNEL = ''

    LASTFM_API_KEY = ''
    MCBOUNCER_KEY = ''
    WOLFRAMALPHA_KEY = ''
    GOOGLESEARCH_KEY = ''

    MINECRAFT_USER = ''
    MINECRAFT_PASSWORD = ''

    BITLY_KEY = ''
    BITLY_USER = ''
