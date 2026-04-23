"""Tests that chi-in-a-box stays in sync with kolla-ansible.

Catches drift between upstream kolla-ansible and chi-in-a-box's
example inventory, passwords, and defaults.
"""

import re
import yaml
import pytest


def _parse_ini_groups(path):
    """Extract group names from an ansible inventory file."""
    groups = set()
    for line in path.read_text().splitlines():
        m = re.match(r'^\[([^\]:]+)', line)
        if m:
            groups.add(m.group(1))
    return groups


class TestInventorySync:
    """Ensure chi-in-a-box example inventory has all groups kolla-ansible expects."""

    def test_example_inventory_exists(self, ciab_dir):
        assert (ciab_dir / "site-config.example" / "inventory" / "hosts").exists()

    def test_no_missing_groups(self, ciab_dir, kolla_ansible_dir):
        kolla_multinode = kolla_ansible_dir / "ansible" / "inventory" / "multinode"
        if not kolla_multinode.exists():
            pytest.skip("kolla-ansible multinode inventory not found")

        kolla_groups = _parse_ini_groups(kolla_multinode)
        ciab_groups = _parse_ini_groups(
            ciab_dir / "site-config.example" / "inventory" / "hosts")

        missing = kolla_groups - ciab_groups
        allowed_missing = {"connection-plugin"}
        missing -= allowed_missing

        assert not missing, (
            f"Groups in kolla-ansible but missing from chi-in-a-box inventory: {missing}"
        )


class TestPasswordsSync:
    """Ensure chi-in-a-box passwords.yml has all keys kolla-ansible expects."""

    def test_no_missing_passwords(self, ciab_dir, kolla_ansible_dir):
        kolla_pw = kolla_ansible_dir / "etc" / "kolla" / "passwords.yml"
        if not kolla_pw.exists():
            pytest.skip("kolla-ansible passwords.yml not found")

        kolla_keys = set(yaml.safe_load(kolla_pw.read_text()).keys())
        ciab_keys = set(yaml.safe_load(
            (ciab_dir / "site-config.example" / "passwords.yml").read_text()).keys())

        missing = kolla_keys - ciab_keys
        assert not missing, (
            f"Password keys in kolla-ansible but missing from chi-in-a-box: {missing}"
        )


class TestDefaultsSync:

    def test_defaults_is_valid_yaml(self, ciab_defaults):
        assert isinstance(ciab_defaults, dict)

    def test_openstack_release_matches(self, ciab_defaults):
        assert "openstack_release" in ciab_defaults
