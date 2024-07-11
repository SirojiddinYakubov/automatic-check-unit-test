import importlib.util


def test_is_installed_psycopg2_binary():
    loader = importlib.util.find_spec('psycopg2-binary')
    assert loader is not None, "psycopg2-binary is not installed"
