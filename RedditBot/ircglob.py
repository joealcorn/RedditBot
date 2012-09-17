
import re

nick_user_host_re = r'^([^!@]+)!([^!@]+)@([^!@]+)$'

def matches(pattern, prefix):
    return glob(pattern).matches(prefix)

class glob(object):
    '''Represents a nick!user@host glob pattern'''
    
    invalid = False
    
    def __init__(self, pattern):
        if glob.is_valid(pattern):
            self.nick, self.user, self.host = self.str_to_tuple(pattern)
        else:
            self.invalid = True
    
    @staticmethod
    def is_valid(nick_user_host):
        return glob.str_to_tuple(nick_user_host) != False
    
    def __eq__(self, other):
        if self.invalid:
            return False
        return (self.nick, self.user, self.host) == (other.nick, other.user, other.host)
    
    def __repr__(self):
        if self.invalid:
            return False
        return 'glob({})'.format(repr((self.nick, self.user, self.host)))
    
    @staticmethod
    def str_to_tuple(nick_user_host):
        '''Convert a "nick!user@host" to (nick, user, host)'''
        match = re.match(nick_user_host_re, nick_user_host, re.I)
        if not match:
            return False
        return match.groups()
    
    @staticmethod
    def pattern_to_re(pattern):
        '''Convert a glob pattern to a regex'''
        r = ''
        for bit in re.finditer(r'(?:[^\?\*]+|\?+|\*+)', pattern, re.I):
            if bit.group().startswith("*"):
                r += '[^!@]*'
            elif bit.group().startswith("?"):
                r += '[^!@]'
                if len(bit.group()) > 1:
                    r += '{%d}' % len(bit.group())
            else:
                r += re.escape(bit.group())
        return '^%s$' % r
    
    @staticmethod
    def matches_piece(pattern, thing):
        '''Return True if thing matches pattern'''
        return re.match(glob.pattern_to_re(pattern), thing, re.I) != None
    
    def matches(self, test):
        '''Return True if 'test' is matched by the pattern we represent'''
        if self.invalid:
            return False
        nick, user, host = self.str_to_tuple(test)
        return self.matches_piece(self.nick, nick) and self.matches_piece(self.user, user) and self.matches_piece(self.host, host)
    
    @staticmethod
    def pattern_to_super_re(pattern):
        '''Like glob.pattern_to_re but for superset testing'''
        r = ''
        for bit in re.finditer(r'(?:[^\?\*]+|\?+|\*+)', pattern, re.I):
            if bit.group().startswith("*"):
                r += '[^!@]*'
            elif bit.group().startswith("?"):
                r += '[^!@*]'
                if len(bit.group()) > 1:
                    r += '{%d}' % len(bit.group())
            else:
                r += re.escape(bit.group())
        return '^%s$' % r
    
    @staticmethod
    def issuper_piece(a, b):
        '''Like glob.matches_piece but for superset testing'''
        return re.match(glob.pattern_to_super_re(a), b, re.I) != None
    
    def issuper(self, other):
        '''Return True if the set of all nick!user@host matched by this glob is a superset of those matched by 'other\''''
        if self.invalid:
            return False
        return self.issuper_piece(self.nick, other.nick) and self.issuper_piece(self.user, other.user) and self.issuper_piece(self.host, other.host)
    
    def issub(self, other):
        '''Return True if the set of all nick!user@host matched by this glob is a subset of those matched by 'other\''''
        if self.invalid:
            return False
        return other.issuper(self)
