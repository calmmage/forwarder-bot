def test_imports():
    from forwarder_bot.app import MyApp
    from forwarder_bot.handler import MyHandler

    assert MyApp
    assert MyHandler
