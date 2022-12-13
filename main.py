# This is a sample Python script.
import socket
import ssl
import asyncio
import time
import yaml

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=nr67zepkjphqf1h5af73wvmhdwebxj&redirect_uri=http://localhost&scope=chat%3Aread+chat%3Aedit

nick = 'gunstrucksbbq'
token = ''
hostname = 'irc.chat.twitch.tv'

def wrapUtf8(s):
    return bytes(s, encoding='utf-8')

def generatePRIVMSG():
    return wrapUtf8(f'PRIVMSG #gunstrucksbbq :hgodLiltilt\n')

def printD(data):
    for v in data.split(r'\r\n'):
        print(f'{v}')

def syncmode():
    with open('creds.yaml') as file:
        creds = yaml.safe_load(file)
        token = creds['token']

    context = ssl.create_default_context()
    with socket.create_connection((hostname, 6697)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
            ssock.sendall(wrapUtf8(f'PASS oauth:{token}\n'))
            ssock.sendall(b'NICK gunstrucksbbq\n')
            printD(str(ssock.recv(1024)))

            ssock.sendall(b'JOIN #gunstrucksbbq\n')
            printD(str(ssock.recv(1024)))

            for idx in range(2):
                ssock.sendall(generatePRIVMSG())
                time.sleep(10)

            while True:
                printD(str(ssock.recv(1024)))

async def processs_custom_events(conn_closed, queuebus):
    while not conn_closed():
        entry = await queuebus.get()
        print(entry)
        queuebus.task_done()
    print('transport closed returning')

async def asyncmode():
    with open('creds.yaml') as file:
        creds = yaml.safe_load(file)
        token = creds['token']
    # for now just a default old security context for SSL
    context = ssl.create_default_context()
    loop = asyncio.get_event_loop()
    # create connection and using Twitch protocol will propagate events in given queue
    queuebus = asyncio.Queue()
    transport, protocol = await loop.create_connection(lambda: TwitchBotClient(queuebus, nick, token), hostname, 6697, ssl=context)
    # our process w/ custom handlers for non-protocol messages
    await processs_custom_events(transport.is_closing, queuebus)
    # try:
    #     print('waiting lost connection')
    #     await on_lost_conn
    # finally:
    #     transport.close()

class TwitchBotClient(asyncio.Protocol):
    def __init__(self, queuebus, nick, token):
        self.queuebus = queuebus
        self.nick = nick
        self.token = token

    def _auth(self):
        self.transport.write(f'PASS oauth:{self.token}\n'.encode())
        self.transport.write(f'NICK {self.nick}\n'.encode())
        self.transport.write(f'JOIN #gunstrucksbbq\n'.encode())

    def connection_made(self, transport):
        print('connected to twitch irc')
        self.transport = transport
        self._auth()

    def data_received(self, data):
        message = data.decode().strip()

        # handle PING/PONG keep alives
        if message == 'PING :tmi.twitch.tv':
            print('got a PING, so we shall PONG!')
            #self.transport.write('PONG :tmi.twitch.tv\n'.encode())
        else:
            self.queuebus.put_nowait(message)

    def connection_lost(self, exc):
        self.transport.close()
        print('connection lost to twitch irc')

if __name__ == '__main__':
    asyncio.run(asyncmode())



# :foo!foo@foo.tmi.twitch.tv PRIVMSG #bar :bleedPurple
# parse up to PRIVMSG, capture using regex, all after as rest to parse in sub regex?

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
