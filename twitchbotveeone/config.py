from schema import Schema, And, Use, Optional
import yaml
import os
from rich import print
from rich.table import Table
import logging


logger = logging.getLogger(__name__)

configschema = Schema({'nickname': And(str, len),
                 'token': And(str),
                 Optional('workercount', default=2): And(Use(int), lambda n: 1 <= n <= 8),
                 'channel': And(str, len)})


def parse_config(configfile):
    if not Schema(os.path.exists).validate(configfile):
        pass

    with open('config.yaml') as file:
        creds = yaml.safe_load(file)
        return BotConfiguration(creds)


class BotConfiguration(object):

    def __init__(self, creds):
        self._config = configschema.validate(creds)
        self.hostname = 'irc.chat.twitch.tv'

    def __getattr__(self, key):
        if key in self._config:
            return self._config[key]
        raise NameError

    def pretty_print(self):
        table = Table(title="Configuration")
        table.add_column("Name", style="magenta")
        table.add_column("Value", style="cyan")
        for k, v in self._config.items():
            table.add_row(k, str(v))
        print(table)
