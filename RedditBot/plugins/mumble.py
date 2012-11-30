from RedditBot import bot

from struct import pack, unpack
import datetime
import socket
import re

# Based on this script found at http://mumble.sourceforge.net/Protocol
# https://gitorious.org/mumble-scripts/mumble-scripts/blobs/master/Non-RPC/mumble-ping.py

server_re = re.compile(r'^\s*([A-Za-z0-9_-]+\.[A-Za-z0-9_.-]+)(?::([0-9]{1,5}))?\s*$')


def get_info(host, port=64738):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)

    buf = pack(">iQ", 0, datetime.datetime.now().microsecond)

    try:
        s.sendto(buf, (host, port))
    except socket.gaierror as e:
        return {'success': False,
                'error': e,
                'message': 'That doesn\'t appear to be a valid hostname'}

    try:
        data, addr = s.recvfrom(1024)
    except socket.timeout as e:
        return {'success': False,
                'error': e,
                'message': 'Timeout'}

    r = unpack(">bbbbQiii", data)

    version = r[1:4]
    ping = (datetime.datetime.now().microsecond - r[4]) / 1000.0

    if ping < 0:
        ping = ping + 1000

    info = {
        'version': '.'.join(str(i) for i in version),
        'ping': ping,
        'users': r[5],
        'max': r[6],
        'bandwidth': r[7],
        'success': True
    }

    return info


@bot.command
def mumble(context):
    '''Usage: .mumble <[host[:port]]>'''
    if context.args.strip() == '':
        context.args = 'mumble.nerd.nu:6162'

    server = server_re.match(context.args)
    if server is None:
        return mumble.__doc__

    if server.group(2) is None:
        thing = get_info(server.group(1))
    else:
        thing = get_info(server.group(1), int(server.group(2)))

    if not thing['success']:
        return 'Couldn\'t reach {0}: {1}'.format(server.group(1), thing['message'])

    return '{0} is up with {users:d}/{max:d} users.'.format(server.group(1), **thing)
