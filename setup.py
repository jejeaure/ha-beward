#!/usr/bin/env python3
"""Home Assistant setup script."""
import os
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """PyTest controller."""

    # Code from here:
    # https://docs.pytest.org/en/latest/goodpractices.html#manual-integration

    # pylint: disable=attribute-defined-outside-init
    def finalize_options(self):
        """Finalize test command options."""
        TestCommand.finalize_options(self)
        # we don't run integration tests which need an actual Beward device
        self.test_args = ["-m", "not integration"]
        self.test_suite = True

    # pylint: disable=import-outside-toplevel,import-error
    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        import shlex

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def load_requirements(filename: str) -> list:
    """Load requirements from file."""
    path = os.path.join(os.path.dirname(__file__), filename)
    imp = re.compile(r"^(-r|--requirement)\s+(\S+)")
    reqs = []
    with open(path, encoding="utf-8") as fptr:
        for i in fptr:
            # pylint: disable=invalid-name
            m = imp.match(i)
            if m:
                reqs.extend(load_requirements(m.group(2)))
            else:
                reqs.append(i)

    return reqs


PROJECT_PACKAGE_NAME = "ha-beward"

PACKAGES = find_packages(exclude=["tests", "tests.*"])

MODULES = list(map(__import__, PACKAGES))
VERSION = ""
for i in MODULES:
    if hasattr(i, "VERSION"):
        VERSION = i.VERSION
        break

REQUIREMENTS = load_requirements("requirements.txt")
TEST_REQUIREMENTS = load_requirements("requirements-tests.txt")

setup(
    name=PROJECT_PACKAGE_NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    cmdclass={"pytest": PyTest},
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
)
