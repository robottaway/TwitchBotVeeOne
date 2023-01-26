import sys

import schema
import rich_click as click
from rich import print
from twitchbotveeone import engine
from twitchbotveeone import config as cfg
import coloredlogs


@click.command()
@click.option('--config', 'configpath', default='config.yml', help='path to config.yml file')
def cli(configpath):
    print(f'booted with config [bold magenta]\'{configpath}\'[/bold magenta]')
    try:
        config = cfg.parse_config(configpath)
    except schema.SchemaWrongKeyError as e:
        print(f'Unable to parse configuration!\n> {e}')
        sys.exit(1)
    config.pretty_print()
    engine.startup(config)


def main():
    coloredlogs.install(level='DEBUG')
    cli()
