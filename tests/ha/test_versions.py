"""Keep the test layers on the Home Assistant release (and pymodbus) they claim.

The in-process layer gets Home Assistant from pytest-homeassistant, whose own
version number is the Home Assistant release it depends on (exactly), the
Docker layer from the image tag in .github/ha-versions/Dockerfile. They are
bumped together (one Dependabot group, see .github/dependabot.yml), and these
tests fail when they drift apart. The package, the installed Home Assistant and
the image tag must all be the same release, patch included.
"""

from __future__ import annotations

import json
import re
from importlib.metadata import version
from pathlib import Path

import homeassistant
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION

DOCKERFILE = Path(__file__).parents[2] / ".github" / "ha-versions" / "Dockerfile"


def test_pytest_homeassistant_is_the_installed_ha_release():
    # pytest-homeassistant's version is "<Home Assistant release>", pinned
    # exactly to the homeassistant package it installs.
    assert version("pytest-homeassistant") == version("homeassistant"), (
        f"pytest-homeassistant {version('pytest-homeassistant')} runs Home "
        f"Assistant {version('homeassistant')}: pin the matching release in "
        "requirements_test.txt"
    )


def test_in_process_ha_matches_docker_image():
    match = re.search(
        r"^FROM\s+\S+:(\d+)\.(\d+)\.(\d+)\s*$", DOCKERFILE.read_text(), re.M
    )
    assert match, f"{DOCKERFILE} must pin a release tag (YYYY.M.P), not latest/beta"
    image = tuple(int(g) for g in match.groups())
    running = (MAJOR_VERSION, MINOR_VERSION, int(PATCH_VERSION))
    assert image == running, (
        "Docker e2e image is Home Assistant "
        f"{'.'.join(map(str, image))}, but pytest-homeassistant runs "
        f"{'.'.join(map(str, running))}: bump both together "
        "(requirements_test.txt and .github/ha-versions/Dockerfile)"
    )


def test_pymodbus_matches_home_assistant():
    # Read the file instead of importing the component: importing it needs
    # modbus_connection, which is not installed.
    manifest = (
        Path(homeassistant.__file__).parent / "components" / "modbus" / "manifest.json"
    )
    wanted = [
        r.partition("==")[2]
        for r in json.loads(manifest.read_text())["requirements"]
        if r.startswith("pymodbus==")
    ]
    assert len(wanted) == 1, "Home Assistant's modbus manifest no longer pins pymodbus"
    assert version("pymodbus") == wanted[0], (
        f"Home Assistant ships pymodbus {wanted[0]}, tests run {version('pymodbus')}: "
        "set pymodbus in requirements_test.txt to the version Home Assistant ships"
    )
