import importlib.util


def test_is_installed_decouple():
    loader = importlib.util.find_spec('decouple')
    assert loader is not None, "decouple is not installed"
