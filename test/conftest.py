
import sys


def pytest_addoption(parser):
    parser.addoption("--include-reference", action="store_true",
                     help="Include the reference design cosim tests")


def pytest_configure(config):
    sys._called_from_test = True


def pytest_unconfigure(config):
    del sys._called_from_test
