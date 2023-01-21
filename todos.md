
# Integration REST API

API for discovering commands for other integrations

ex
configure integration url

    integrations:
        diceroll: somehost:someport/diceroll/integrate

on boot call integration

    GET somehost:someport/diceroll/integrate
    > { 'commands': ['diceroll'] }

# Logging

* Research and pick logging api for project
* Implement logging with configurable logging handlers