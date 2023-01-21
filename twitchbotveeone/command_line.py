import rich_click as click
from rich import print
from twitchbotveeone import engine
from twitchbotveeone import config as cfg


@click.command()
@click.option('--nickname', help='nick name of bot')
@click.option('--config', 'configpath', default='config.yml', help='path to config.yml file')
def cli(nickname, configpath):
    print(f'running with config [bold magenta]\'{configpath}\'[/bold magenta], nickname [blue]{nickname}[/blue]')
    config = cfg.parseConfig(configpath)
    engine.startup(config)


def main():
    cli()
