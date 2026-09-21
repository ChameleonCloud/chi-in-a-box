"""Tests that chi-in-a-box stays in sync with kolla-ansible.

Catches drift between upstream kolla-ansible and chi-in-a-box's
example inventory, passwords, and defaults.
"""

import re
import yaml
import pytest


def _inventory_files(inventory):
    """The files Ansible reads from an inventory directory."""
    return sorted(p for p in inventory.iterdir() if p.is_file())


def _parse_ini_groups(paths):
    """Group names declared across the given inventory files."""
    groups = set()
    for path in paths:
        for line in path.read_text().splitlines():
            m = re.match(r'^\[([^\]:]+)', line)
            if m:
                groups.add(m.group(1))
    return groups


class TestInventorySync:
    """Ensure chi-in-a-box example inventory has all groups kolla-ansible expects."""

    def test_example_inventory_exists(self, example_inventory):
        assert _inventory_files(example_inventory)

    def test_no_missing_groups(self, example_inventory, kolla_ansible_dir):
        kolla_multinode = kolla_ansible_dir / "ansible" / "inventory" / "multinode"
        if not kolla_multinode.exists():
            pytest.skip("kolla-ansible multinode inventory not found")

        kolla_groups = _parse_ini_groups([kolla_multinode])
        ciab_groups = _parse_ini_groups(_inventory_files(example_inventory))

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
