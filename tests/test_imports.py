def test_imports():
    from forwarder_bot.app import App
    from forwarder_bot.handler import router, compose_messages

    assert App
    assert router
    assert compose_messages
