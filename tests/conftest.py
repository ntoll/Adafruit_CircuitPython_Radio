import sys
from unittest.mock import MagicMock


# Could this be taken from a configuration setting..?
MOCK_MODULES = [
    "adafruit_ble.BLERadio",
    "adafruit_ble.advertising.adafruit.AdafruitRadio",
]


def mock_imported_modules():
    """
    Mocks away the modules named in MOCK_MODULES.
    """
    module_paths = set()
    for m in MOCK_MODULES:
        namespaces = m.split(".")
        ns = []
        for n in namespaces:
            ns.append(n)
            module_paths.add(".".join(ns))
    for m_path in module_paths:
        sys.modules[m_path] = MagicMock()


def pytest_runtest_setup(item):
    """
    Recreates afresh the mocked away modules so state between tests remains
    isolated.
    """
    mock_imported_modules()


# Needed to stop ImportError when importing module under test.
mock_imported_modules()
