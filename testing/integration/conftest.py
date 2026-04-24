"""Fixtures for genconfig integration tests.

Builds a site-config from site-config.example plus a test profile
(inventory + host_vars overlays, defaults merged via the same yq
expression cc-ansible uses at deploy time), then runs `cc-ansible
genconfig` end-to-end. A failure here means rendered service config
would break on a real host.

No profile parametrization yet — a single synthetic _base profile is
enough to prove the pipeline works. A profile matrix (baremetal/kvm)
is a later PR.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

CIAB_DIR = Path(__file__).resolve().parents[2]
BASE_PROFILE_DIR = CIAB_DIR / "testing" / "profiles" / "_base"


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


def _build_site_config(dest, profile_dir):
    shutil.copytree(CIAB_DIR / "site-config.example", dest)

    # Substitute <host> -> localhost in the example inventory. [compute]
    # is left empty, matching site-config.example; compute-side templates
    # (nova-compute.conf etc.) will be exercised by profiles that populate
    # [compute] with real hosts (e.g. the kvm profile).
    hosts = dest / "inventory" / "hosts"
    hosts.write_text(
        hosts.read_text().replace("<host>", "localhost ansible_connection=local")
    )

    # Overlay profile inventory and host_vars. shutil.copytree with
    # dirs_exist_ok replaces files at matching paths. Real site profiles
    # (kvm, baremetal) ship pre-expanded inventory that fully replaces
    # site-config.example's hosts; _base ships only host_vars overlays.
    profile_inv = profile_dir / "inventory"
    if profile_inv.exists():
        shutil.copytree(profile_inv, dest / "inventory", dirs_exist_ok=True)

    (dest / "defaults.yml").write_text(
        yaml.dump(_merge_yaml([profile_dir / "defaults.yml"]))
    )

    subprocess.run(
        ["kolla-genpwd", "-p", str(dest / "passwords.yml")],
        check=True,
    )
    (dest / "vault_password").write_text("dummy")


@pytest.fixture(scope="session")
def install_deps():
    if not (CIAB_DIR / "venv" / "bin" / "kolla-ansible").exists():
        subprocess.run(
            [str(CIAB_DIR / "cc-ansible"), "install_deps"],
            check=True,
        )


@pytest.fixture(scope="session")
def genconfig_output(install_deps, tmp_path_factory):
    """Run genconfig once per session against the _base profile and return
    the output directory.

    A copy is preserved at $CIAB_PRESERVED_OUTPUT/_base/ (default:
    testing/output/_base/) so the most recent render is always available
    as a reference snapshot — useful both for debugging a failed test and
    as an example of what default-templated config looks like."""
    workdir = tmp_path_factory.mktemp("_base")
    site_dir = workdir / "site-config"
    output_dir = workdir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    _build_site_config(site_dir, BASE_PROFILE_DIR)

    env = {**os.environ, "CC_ANSIBLE_SITE": str(site_dir)}
    subprocess.run(
        [str(CIAB_DIR / "cc-ansible"), "genconfig",
         "--extra", f"node_config_directory={output_dir}"],
        env=env, cwd=str(CIAB_DIR), check=True,
    )

    preserve_root = Path(
        os.environ.get("CIAB_PRESERVED_OUTPUT", CIAB_DIR / "testing" / "output")
    )
    preserved = preserve_root / "_base"
    if preserved.exists():
        shutil.rmtree(preserved)
    preserved.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(output_dir, preserved)

    return output_dir
