"""Integration tests for cc-ansible genconfig.

The harness assembles a site-config from site-config.example plus one
or more profile fragments under testing/profiles/, then runs
`cc-ansible genconfig` and exposes the result to tests.
"""

import configparser
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

# Repo root, the directory holding all profile fragments, and the
# shared base fragment every profile layers on top of.
CIAB_DIR = Path(__file__).resolve().parents[2]
PROFILES_DIR = CIAB_DIR / "testing" / "profiles"
BASE_PROFILE_DIR = PROFILES_DIR / "_base"


class GenconfigResult:
    """Read helpers for a rendered genconfig output directory."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def ini(self, service, filename="") -> configparser.ConfigParser:
        """Return a parsed ConfigParser for a rendered .conf file.
        filename defaults to the service's base name + .conf
        (e.g. 'blazar-manager' -> 'blazar.conf')."""
        if not filename:
            filename = service.split("-")[0] + ".conf"
        conf = configparser.ConfigParser(strict=False, allow_no_value=True)
        conf.read(self.output_dir / service / filename)
        return conf

    def text(self, service, filename) -> str:
        """Read a rendered file under <service>/<filename> as raw text."""
        return (self.output_dir / service / filename).read_text()

    def services(self) -> list:
        """List the service directories genconfig rendered."""
        return [d.name for d in self.output_dir.iterdir() if d.is_dir()]


def _merge_yaml(files):
    """Deep-merge YAML files via the same yq expression cc-ansible uses
    at deploy time (see cc-ansible's globals.yml build step)."""
    if not files:
        return {}
    result = subprocess.run(
        ["yq", "eval-all", ". as $item ireduce ({}; . * $item)",
         *[str(f) for f in files]],
        capture_output=True, text=True, check=True,
    )
    return yaml.safe_load(result.stdout) or {}


def _build_site_config(dest, profile_dirs):
    """Assemble a site-config at `dest` from base and profiles.

    Follows cc-ansible init flow, taking site-config.example and
    overlaying fragments from _base and a given profile.
    Uses ansible to merge inventory files, and `yq` for
    defaults.yml, following how cc-ansible does it.
    """
    shutil.copytree(CIAB_DIR / "site-config.example", dest)

    # Substitute <host> with localhost in the example inventory.
    hosts = dest / "inventory" / "hosts"
    hosts.write_text(
        hosts.read_text().replace("<host>", "localhost ansible_connection=local")
    )

    # Overlay each profile's inventory/ on top. Ansible reads inventory
    # directories, so new files add and matching paths replace.
    for profile_dir in profile_dirs:
        profile_inv = profile_dir / "inventory"
        if profile_inv.exists():
            shutil.copytree(profile_inv, dest / "inventory", dirs_exist_ok=True)

    # Deep-merge defaults.yml layers in order (later overrides earlier).
    defaults_files = [
        p / "defaults.yml" for p in profile_dirs
        if (p / "defaults.yml").exists()
    ]
    (dest / "defaults.yml").write_text(yaml.dump(_merge_yaml(defaults_files)))

    subprocess.run(
        ["kolla-genpwd", "-p", str(dest / "passwords.yml")],
        check=True,
    )
    (dest / "vault_password").write_text("dummy")


def _run_genconfig(tmp_path, profile_dirs, preserve_name):
    site_dir = tmp_path / "site-config"
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    _build_site_config(site_dir, profile_dirs)

    env = {**os.environ, "CC_ANSIBLE_SITE": str(site_dir)}
    subprocess.run(
        [str(CIAB_DIR / "cc-ansible"), "genconfig",
         "--extra", f"node_config_directory={output_dir}"],
        env=env, cwd=str(CIAB_DIR), check=True,
    )

    preserve_root = Path(
        os.environ.get("CIAB_PRESERVED_OUTPUT", CIAB_DIR / "testing" / "output")
    )
    preserved = preserve_root / preserve_name
    if preserved.exists():
        shutil.rmtree(preserved)
    preserved.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(output_dir, preserved)

    return GenconfigResult(output_dir)

@pytest.fixture(scope="session")
def minimal_config(tmp_path_factory):
    """Assembled site-config with the _base fragment only. Proves
    site-config.example renders end-to-end."""
    return _run_genconfig(
        tmp_path_factory.mktemp("minimal"),
        [BASE_PROFILE_DIR],
        preserve_name="minimal",
    )


@pytest.fixture(scope="session")
def kvm_config(tmp_path_factory):
    """Assembled site-config with _base + kvm fragments."""
    return _run_genconfig(
        tmp_path_factory.mktemp("kvm"),
        [BASE_PROFILE_DIR, PROFILES_DIR / "kvm"],
        preserve_name="kvm",
    )
