# About this file, see
# https://docs.pytest.org/en/6.2.x/writing_plugins.html#localplugin

def pytest_generate_tests(metafunc):
    if "index_allowlist" in metafunc.fixturenames:
        metafunc.parametrize("index_allowlist", [False, True])
