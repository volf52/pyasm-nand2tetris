from pyasm.cli import hello


def test_hello():
    assert hello() == "hello world!"
