# This is a sample Python script.
import ssl
import asyncio
from asyncio.exceptions import CancelledError

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=nr67zepkjphqf1h5af73wvmhdwebxj&redirect_uri=http://localhost&scope=chat%3Aread+chat%3Aedit


async def processs_custom_events(queuebus):
    while True:
        try:
            entry = await queuebus.get()
            # todo is parse the event and then take any action
            print(entry)
            queuebus.task_done()
        except (CancelledError, KeyboardInterrupt):
            print("canceled task!")
            break


async def asyncmode(config):
    # create the items required to setup proto+transport
    context = ssl.create_default_context()
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    # create connection and using Twitch protocol will propagate events in given queue
    queuebus = asyncio.Queue()
    transport, protocol = await loop.create_connection(lambda: TwitchBotClient(on_con_lost, queuebus, config), config.hostname, 6697, ssl=context)

    # our process w/ custom workers for non-protocol messages
    workers = []
    for i in range(config.workercount):
        worker = asyncio.create_task(processs_custom_events(queuebus))
        workers.append(worker)

    try:
        print('waiting on a broken connection...')
        await on_con_lost
    except KeyboardInterrupt:
        pass
    finally:
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        transport.close()


class TwitchBotClient(asyncio.Protocol):
    def __init__(self, on_conn_lost, queuebus, config):
        self.on_conn_lost = on_conn_lost
        self.queuebus = queuebus
        self.config = config
        self.transport = None

    def _auth(self):
        self.transport.write(f'PASS oauth:{self.config.token}\n'.encode())
        self.transport.write(f'NICK {self.config.nickname}\n'.encode())
        self.transport.write(f'JOIN #{self.config.channel}\n'.encode())

    def connection_made(self, transport):
        print('connected to twitch irc')
        self.transport = transport
        self._auth()

    def data_received(self, data):
        message = data.decode().strip()

        # handle PING/PONG keep alives
        if message == 'PING :tmi.twitch.tv':
            print('got a PING, so we shall PONG!')
            self.transport.write('PONG :tmi.twitch.tv\n'.encode())
        else:
            self.queuebus.put_nowait(message)

    def connection_lost(self, exc):
        print('connection lost to twitch irc')
        self.on_conn_lost.set_result(True)


def startup(config):
    try:
        # this solves a nuisence with RuntimeError being thrown when the app is stopped
        asyncio.run(asyncmode(config))
        print('Bot finished at ...')
    except KeyboardInterrupt:
        pass

# parse up to PRIVMSG, capture using regex, all after as rest to parse in sub regex?

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
