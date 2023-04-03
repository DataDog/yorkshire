def pytest_generate_tests(metafunc):
    if "index_allowlist" in metafunc.fixturenames:
        metafunc.parametrize("index_allowlist", [False, True])
