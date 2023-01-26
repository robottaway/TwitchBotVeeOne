import ssl
import asyncio
from asyncio.exceptions import CancelledError
import logging


logger = logging.getLogger(__name__)


async def processs_custom_events(queuebus):
    while True:
        try:
            entry = await queuebus.get()
            # todo is parse the event and then take any action
            logger.debug(entry)
            queuebus.task_done()
        except (CancelledError, KeyboardInterrupt):
            logger.info("canceled task!")
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
    logger.info(f'Spinning up {config.workercount} workers')
    for i in range(config.workercount):
        worker = asyncio.create_task(processs_custom_events(queuebus))
        workers.append(worker)

    try:
        logger.info('waiting on a broken connection...')
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
        logger.info('connected to twitch irc')
        self.transport = transport
        self._auth()

    def data_received(self, data):
        message = data.decode().strip()

        # handle PING/PONG keep alives
        if message == 'PING :tmi.twitch.tv':
            logger.info('got a PING, so we shall PONG!')
            self.transport.write('PONG :tmi.twitch.tv\n'.encode())
        else:
            self.queuebus.put_nowait(message)

    def connection_lost(self, exc):
        logger.info('connection lost to twitch irc')
        self.on_conn_lost.set_result(True)


def startup(config):
    try:
        # this solves a nuisance with RuntimeError being thrown when the app is stopped
        asyncio.run(asyncmode(config))
        logger.info('Bot finished at ...')
    except KeyboardInterrupt:
        pass
