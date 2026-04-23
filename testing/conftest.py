"""Shared paths for all chi-in-a-box tests.

pytest loads conftest.py files hierarchically, so these fixtures
are available to both unit/ and integration/ tests automatically.
"""

import yaml
import pytest
from pathlib import Path

CIAB_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def ciab_dir():
    return CIAB_DIR


@pytest.fixture(scope="session")
def ciab_defaults_path():
    return CIAB_DIR / "kolla" / "defaults.yml"


@pytest.fixture(scope="session")
def ciab_defaults(ciab_defaults_path):
    return yaml.safe_load(ciab_defaults_path.read_text())


@pytest.fixture(scope="session")
def kolla_ansible_dir():
    path = CIAB_DIR / "src" / "kolla-ansible"
    if not path.exists():
        pytest.skip("kolla-ansible submodule not initialized")
    return path
