import pytest


def test_imports():
    from forwarder_bot.lib import MyApp, MainHandler

    assert MyApp
    assert MainHandler
