"""Fixtures for integration tests. Requires cc-ansible install_deps.

Each profile is a directory under testing/profiles/. A site-config is
assembled by copying site-config.example, overlaying _base/ inventory,
then the named profile. defaults.yml files are deep-merged via the same
yq expression cc-ansible uses at deploy time, so test merge semantics
match prod.

To add a profile: create testing/profiles/<name>/defaults.yml and add
<name> to PROFILES below.
"""

import configparser
import os
import shutil
import subprocess
import yaml
import pytest
from pathlib import Path

# conftest.py files aren't importable modules — derive paths inline.
CIAB_DIR = Path(__file__).resolve().parents[2]
PROFILES_DIR = CIAB_DIR / "testing" / "profiles"

PROFILES = ["baremetal", "kvm"]


class GenconfigResult:
    """Parsed genconfig output."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def ini(self, service, filename="") -> configparser.ConfigParser:
        if not filename:
            filename = service.split("-")[0] + ".conf"
        conf = configparser.ConfigParser(strict=False, allow_no_value=True)
        conf.read(self.output_dir / service / filename)
        return conf

    def text(self, service, filename) -> str:
        return (self.output_dir / service / filename).read_text()

    def services(self) -> list:
        return [d.name for d in self.output_dir.iterdir() if d.is_dir()]


def _merge_defaults(files):
    """Deep-merge YAML files. Same yq expression cc-ansible uses at deploy
    time to merge kolla/defaults.yml + site/defaults.yml into globals.yml,
    so test merge semantics can't silently diverge from prod.
    """
    if not files:
        return {}
    result = subprocess.run(
        ["yq", "eval-all", ". as $item ireduce ({}; . * $item)",
         *[str(f) for f in files]],
        capture_output=True, text=True, check=True,
    )
    return yaml.safe_load(result.stdout) or {}


def _build_site_config(tmp_path, profile):
    site_dir = tmp_path / "site-config"
    shutil.copytree(CIAB_DIR / "site-config.example", site_dir)

    assert str(site_dir).startswith(str(tmp_path)), \
        f"Refusing to modify {site_dir} outside tmpdir {tmp_path}"

    # Overlay inventory: _base/ (synthetic localhost, connection=local)
    # then profile-specific overrides if any. Profile inventory dirs are
    # optional — _base is the only one we ship today.
    inv_dir = site_dir / "inventory"
    (inv_dir / "hosts").unlink(missing_ok=True)
    for layer in ["_base", profile]:
        src = PROFILES_DIR / layer / "inventory"
        if not src.exists():
            continue
        for f in src.rglob("*"):
            if f.is_file():
                out = inv_dir / f.relative_to(src)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(f, out)

    # Deep-merge _base + profile defaults in overlay order.
    defaults_files = [
        PROFILES_DIR / layer / "defaults.yml"
        for layer in ["_base", profile]
        if (PROFILES_DIR / layer / "defaults.yml").exists()
    ]
    (site_dir / "defaults.yml").write_text(
        yaml.dump(_merge_defaults(defaults_files))
    )

    subprocess.run(
        ["kolla-genpwd", "-p", str(site_dir / "passwords.yml")],
        check=True,
    )
    (site_dir / "vault_password").write_text("dummy")

    return site_dir


def run_genconfig(tmp_path, profile, preserve_as=None):
    site_dir = _build_site_config(tmp_path, profile)
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    env = {**os.environ, "CC_ANSIBLE_SITE": str(site_dir)}
    subprocess.run(
        [str(CIAB_DIR / "cc-ansible"), "genconfig",
         "--extra", f"node_config_directory={output_dir}"],
        env=env, text=True, check=True,
        cwd=str(CIAB_DIR),  # cc-ansible reads ./kolla-skip-tags relative to CWD.
    )

    if preserve_as:
        preserved = CIAB_DIR / "testing" / "output" / preserve_as
        if preserved.exists():
            shutil.rmtree(preserved)
        preserved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(output_dir, preserved)

    return GenconfigResult(output_dir)


@pytest.fixture(scope="session")
def install_deps():
    venv = CIAB_DIR / "venv"
    if not (venv / "bin" / "kolla-ansible").exists():
        subprocess.run(
            [str(CIAB_DIR / "cc-ansible"), "install_deps"],
            check=True,
        )


@pytest.fixture(scope="session", params=PROFILES)
def profile(request):
    return request.param


@pytest.fixture(scope="session")
def profile_config(install_deps, profile, tmp_path_factory):
    return run_genconfig(
        tmp_path_factory.mktemp(profile), profile, preserve_as=profile,
    )
