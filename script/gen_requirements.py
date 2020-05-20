#!/usr/bin/env python3
"""Generate an updated requirements.txt."""
import os
import re
import sys
from pathlib import Path

from script.gen_requirements_all import (
    diff_file,
    IGNORE_PIN,
    URL_PIN,
    requirements_pre_commit_output,
    comment_requirement,
)
from script.hassfest.model import Integration


def gather_recursive_requirements(domain, seen=None):
    """Recursively gather requirements from a module."""
    if seen is None:
        seen = set()

    seen.add(domain)
    integration = Integration(Path(f"custom_components/{domain}"))
    integration.load_manifest()
    reqs = set(integration.requirements)
    for dep_domain in integration.dependencies:
        reqs.update(gather_recursive_requirements(dep_domain, seen))
    return reqs


def process_requirements(errors, module_requirements, package, reqs):
    """Process all of the requirements."""
    for req in module_requirements:
        if "://" in req:
            errors.append(f"{package}[Only pypi dependencies are allowed: {req}]")
        if (
            req.partition("==")[1] == ""
            and req.partition("~=")[1] == ""
            and req not in IGNORE_PIN
        ):
            errors.append(f"{package}[Please pin requirement {req}, see {URL_PIN}]")
        reqs.setdefault(req, []).append(package)


def gather_requirements_from_manifests(errors, reqs):
    """Gather all of the requirements from manifests."""
    integrations = Integration.load_dir(Path("custom_components"))
    for domain in sorted(integrations):
        integration = integrations[domain]

        if not integration.manifest:
            errors.append(f"The manifest for integration {domain} is invalid.")
            continue

        process_requirements(
            errors, integration.requirements, f"custom_components.{domain}", reqs
        )


def gather_modules():
    """Collect the information."""
    reqs = {}

    errors = []

    gather_requirements_from_manifests(errors, reqs)

    for key in reqs:
        reqs[key] = sorted(reqs[key], key=lambda name: (len(name.split(".")), name))

    if errors:
        print("******* ERROR")
        print("Errors while importing: ", ", ".join(errors))
        return None

    return reqs


def read_requirements(filepath) -> list:
    """Read requirements from pip file."""
    reqs = []
    comment = re.compile(r"^\s+#")
    with open(filepath) as fptr:
        for i in fptr:
            if not comment.match(i):
                reqs.append(i)
    return reqs


def get_homeassistant_req(filepath):
    """Get required HA package version from pip file."""
    hass = re.compile(r"^homeassistant\W")
    reqs = filter(lambda req: hass.match(req), read_requirements(filepath))
    return "".join(reqs)


def generate_requirements_list(reqs):
    """Generate a pip file based on requirements."""
    output = []
    for pkg, requirements in sorted(reqs.items(), key=lambda item: item[0]):
        if comment_requirement(pkg):
            output.append(f"# {pkg}\n")
        else:
            output.append(f"{pkg}\n")
    return "".join(output)


def requirements_output(reqs):
    """Generate output for requirements_all."""
    output = []
    output.append(get_homeassistant_req("requirements.txt"))
    output.append(generate_requirements_list(reqs))

    return "".join(output)


def main(validate):
    """Run the script."""
    if not os.path.isfile("requirements.txt"):
        print("Run this from HA root dir")
        return 1

    data = gather_modules()

    if data is None:
        return 1

    reqs_file = requirements_output(data)
    reqs_pre_commit_file = requirements_pre_commit_output()

    files = (
        ("requirements.txt", reqs_file),
        ("requirements-pre-commit.txt", reqs_pre_commit_file),
    )

    if validate:
        errors = []

        for filename, content in files:
            diff = diff_file(filename, content)
            if diff:
                errors.append("".join(diff))

        if errors:
            print("ERROR - FOUND THE FOLLOWING DIFFERENCES")
            print()
            print()
            print("\n\n".join(errors))
            print()
            print("Please run python3 -m script.gen_requirements")
            return 1

        return 0

    for filename, content in files:
        Path(filename).write_text(content)

    return 0


if __name__ == "__main__":
    _VAL = sys.argv[-1] == "validate"
    sys.exit(main(_VAL))
