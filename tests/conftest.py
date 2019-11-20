"""
This file ensures everything is in place to run PyTest based unit tests against
the adafruit_radio module. It works by using Python's mock library to add
MagicMock objects to sys.modules for the modules which are not available to
standard Python because they're CircuitPython only modules.

Such mocking happens as soon as this conftest.py file is imported (so the
mocked modules exist in sys.modules before the module to be tested is
imported), and immediately before each test function is evaluated (so changes
to state remain isolated between tests).
"""
import sys
from unittest.mock import MagicMock

# Add fully qualified namespace paths to things that are imported, but which
# should be mocked away. For instance, modules which are available in
# CircuitPython but not standard Python.
MOCK_MODULES = [
    "adafruit_ble.BLERadio",
    "adafruit_ble.advertising.adafruit.AdafruitRadio",
]


def mock_imported_modules():
    """
    Mocks away the modules named in MOCK_MODULES, so the module under test
    can be imported with modules which may not be available.
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
    Called immediately before any test function is called.

    Recreates afresh the mocked away modules so state between tests remains
    isolated.
    """
    mock_imported_modules()


# Initial mocking needed to stop ImportError when importing module under test.
mock_imported_modules()
