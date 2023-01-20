from setuptools import setup

setup(
    name='TwitchBot',
    version='0.1',
    packages=['twitchbotveeone'],
    url='',
    license='',
    author='R. Ottaway',
    author_email='noone@none.net',
    description='Twitch chat bot',
    entry_points={
        'console_scripts': ['twitchbotveeone=twitchbotveeone.command_line:main'],
    },
)
