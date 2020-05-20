#!/usr/bin/env python3
"""Setup tests environment for custom component."""
import ast
import json
import logging
import os
import pathlib
import sys
import tempfile
import urllib.request

# pylint: disable=invalid-name
from homeassistant.const import __version__ as HA_VERSION

logging.getLogger(__name__).addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

FILES = [
    "async_mock.py",
    "common.py",
    "conftest.py",
    "ignore_uncaught_exceptions.py",
    "test_util/aiohttp.py",
]

required_components = set()


def get_components():
    """Return list of required HA components."""
    components = required_components.copy()
    for i in FILES:
        with open(f"tests/{i}") as fptr:
            tree = ast.parse(fptr.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for subnode in node.names:
                        _LOGGER.debug(subnode.name)
                        if str(subnode.name).startswith("homeassistant.components."):
                            components.add(str(subnode.name)[25:])
                if isinstance(node, ast.ImportFrom):
                    if node.module == "homeassistant.components":
                        for subnode in node.names:
                            _LOGGER.debug("%s.%s", node.module, subnode.name)
                            components.add(subnode.name)
    return list(components)


def get_requirements() -> list:
    """Return list of required packages for required HA components."""
    try:
        from homeassistant import components  # pylint: disable=import-outside-toplevel
    except ImportError:
        return []

    reqs = set()
    for domain in get_components():
        for base in components.__path__:  # type: ignore
            manifest_path = pathlib.Path(base) / domain / "manifest.json"

            if not manifest_path.is_file():
                continue

            try:
                manifest = json.loads(manifest_path.read_text())
            except ValueError as err:
                _LOGGER.error(
                    "Error parsing manifest.json file at %s: %s", manifest_path, err
                )
                continue
            reqs.update(manifest.get("requirements", []))
    return list(reqs)


def update_ha_files():
    """Copy files from HomeAssistant core tests."""
    with urllib.request.urlopen(
        "https://api.github.com/repos/home-assistant/core/tags"
    ) as url:
        tags = json.loads(url.read().decode())

    commit = None
    for i in tags:
        if i.get("name") == HA_VERSION:
            commit = i["commit"]["sha"]

    tmpfile = tempfile.mkstemp()[1]
    os.system(
        "wget -nv --show-progress "
        f"-O{tmpfile} https://github.com/home-assistant/core/archive/{commit}.tar.gz"
    )
    tests = f"core-{commit}/tests/"
    files = " ".join(tests + i for i in FILES)
    os.system(f"tar xzf {tmpfile} {files} -C tests --strip-components=1")
    os.system(f"rm {tmpfile}")

    with open("tests/ha-version", "w") as fptr:
        fptr.write(HA_VERSION)

    with open("tests/requirements-ha.txt", "w") as fptr:
        fptr.write("\n".join(get_requirements()))


# Add required by user components if exists
required_components.update(sys.argv[1:])
_LOGGER.debug("Required components: %s", ", ".join(required_components))

match_version = False
try:
    with open("tests/ha-version") as file:
        match_version = file.read() == HA_VERSION
except FileNotFoundError:
    pass

match_files = True
for file in FILES:
    match_files &= os.path.isfile(f"tests/{file}")

# print(f'match_version: {match_version}')
# print(f'match_files: {match_files}')
if not match_version or not match_files:
    update_ha_files()

os.system("pip install -r tests/requirements-ha.txt")
