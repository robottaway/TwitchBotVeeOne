import rich_click as click
from rich import print
from twitchbotveeone import engine


@click.command()
@click.option('--nickname', help='nick name of bot')
@click.option('--config', default='config.yml', help='path to config.yml file')
def cli(nickname, config):
    print(f'running with config [bold magenta]\'{config}\'[/bold magenta], nickname [blue]{nickname}[/blue]')
    engine.startup()


def main():
    cli()
