"""Fixtures for integration tests. Requires cc-ansible install_deps."""

import configparser
import os
import shutil
import subprocess
import yaml
import pytest
from pathlib import Path

# Derived here rather than imported — conftest files aren't importable as modules.
CIAB_DIR = Path(__file__).resolve().parents[2]


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


def _build_site_config(tmp_path, overrides, extra_files=None):
    site_dir = tmp_path / "site-config"
    shutil.copytree(CIAB_DIR / "site-config.example", site_dir)

    (site_dir / "defaults.yml").write_text(yaml.dump(overrides))

    # Safety: only modify files inside the pytest tmpdir
    assert str(site_dir).startswith(str(tmp_path)), \
        f"Refusing to modify {site_dir} outside tmpdir {tmp_path}"

    # Replace example inventory with test inventory (localhost, no SSH)
    inv_dir = site_dir / "inventory"
    (inv_dir / "hosts").unlink(missing_ok=True)
    test_inv = CIAB_DIR / "testing" / "inventory"
    for f in test_inv.iterdir():
        if f.is_dir():
            shutil.copytree(f, inv_dir / f.name, dirs_exist_ok=True)
        else:
            shutil.copy(f, inv_dir / f.name)

    for rel_path, content in (extra_files or {}).items():
        dest = site_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            dest.write_text(content)
        else:
            dest.write_text(yaml.dump(content))

    pw_file = site_dir / "passwords.yml"
    subprocess.run(
        ["kolla-genpwd", "-p", str(pw_file)],
        check=True, capture_output=True,
    )
    (site_dir / "vault_password").write_text("dummy")

    return site_dir


def run_genconfig(tmp_path, overrides, extra_files=None):
    site_dir = _build_site_config(tmp_path, overrides, extra_files)
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    env = {**os.environ, "CC_ANSIBLE_SITE": str(site_dir)}
    result = subprocess.run(
        [str(CIAB_DIR / "cc-ansible"), "genconfig",
         "--extra", f"node_config_directory={output_dir}"],
        env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"genconfig failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    return GenconfigResult(output_dir)


# --- Profile variable sets ---

MINIMAL_VARS = {
    "kolla_internal_vip_address": "172.18.200.254",
    "kolla_external_vip_address": "172.18.200.254",
    "network_interface": "eth0",
    "neutron_external_interface": "eth1",
    "kolla_base_distro": "ubuntu",
    # Override the default /etc/ansible/venv/bin/python which is created by
    # bootstrap-servers on real hosts. In test we just use system python3.
    "ansible_python_interpreter": "python3",
}

KVM_VARS = {
    **MINIMAL_VARS,
    "openstack_region_name": "TestKVM",
    "enable_ironic": False,
    "nova_compute_virt_type": "kvm",
    "blazar_enable_flavor_reservation": True,
    "blazar_flavor_reservation_trait": "CUSTOM_TEST_TRAIT",
    "blazar_enable_host_reservation": False,
    "enable_blazar_allocation_enforcement": True,
    "blazar_filter_vm_hosts": True,
    "blazar_filter_ironic_hosts": True,
}

KVM_GPU_VARS = {**KVM_VARS}

KVM_GPU_EXTRA_FILES = {
    "inventory/host_vars/localhost.yml": yaml.dump({
        "gpu": True,
        "node_reserved_memory_mb": 65536,
        "nova_pci_device_spec": [
            {"vendor_id": "10de", "product_id": "2339",
             "traits": "CUSTOM_GPU_H100,CUSTOM_GPU"},
        ],
        "nova_pci_alias": [
            {"name": "h100", "vendor_id": "10de",
             "product_id": "2339", "device_type": "type-PF"},
        ],
    }),
}


# --- Fixtures ---

@pytest.fixture(scope="session")
def install_deps():
    venv = CIAB_DIR / "venv"
    if not (venv / "bin" / "kolla-ansible").exists():
        subprocess.run(
            [str(CIAB_DIR / "cc-ansible"), "install_deps"],
            check=True,
        )


@pytest.fixture(scope="session")
def minimal_config(install_deps, tmp_path_factory):
    return run_genconfig(tmp_path_factory.mktemp("minimal"), MINIMAL_VARS)


@pytest.fixture(scope="session")
def kvm_config(install_deps, tmp_path_factory):
    return run_genconfig(tmp_path_factory.mktemp("kvm"), KVM_VARS)


@pytest.fixture(scope="session")
def kvm_gpu_config(install_deps, tmp_path_factory):
    return run_genconfig(
        tmp_path_factory.mktemp("kvm-gpu"), KVM_GPU_VARS, KVM_GPU_EXTRA_FILES,
    )
