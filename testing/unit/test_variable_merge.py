"""Tests for the yq variable merge logic used by cc-ansible.

cc-ansible merges kolla/defaults.yml + site-config/defaults.yml via:
    yq eval-all '. as $item ireduce ({}; . * $item)' base.yml site.yml

This is a deep merge where site values override base values.
Lists are replaced entirely (not appended).
"""


class TestMergePrecedence:
    """Site-config overrides take precedence over chi-in-a-box defaults."""

    def test_scalar_override_wins(self, yq_merge):
        merged = yq_merge({"blazar_enable_flavor_reservation": True})
        assert merged["blazar_enable_flavor_reservation"] is True

    def test_base_preserved_when_not_overridden(self, yq_merge):
        merged = yq_merge({})
        assert "enable_mariadb" in merged

    def test_string_override(self, yq_merge):
        merged = yq_merge({"openstack_region_name": "KVM@TACC"})
        assert merged["openstack_region_name"] == "KVM@TACC"


class TestMergeSemantics:
    """yq ireduce replaces lists, deep-merges dicts."""

    def test_list_replaced_not_appended(self, yq_merge):
        merged = yq_merge({
            "horizon_custom_themes": [{"name": "custom", "label": "Custom"}],
        })
        assert len(merged["horizon_custom_themes"]) == 1
        assert merged["horizon_custom_themes"][0]["name"] == "custom"

    def test_empty_override_is_noop(self, yq_merge, ciab_defaults):
        merged = yq_merge({})
        for key in ["enable_blazar", "enable_nova", "enable_keystone"]:
            assert merged[key] == ciab_defaults[key]


class TestDefaultsCompleteness:
    """Verify that kolla/defaults.yml defines expected variables."""

    def test_blazar_defaults_exist(self, ciab_defaults):
        for key in [
            "enable_blazar",
            "blazar_minutes_before_end_lease",
            "blazar_default_max_lease_duration",
            "blazar_email_relay",
        ]:
            assert key in ciab_defaults, f"Missing default: {key}"

    def test_nova_defaults_exist(self, ciab_defaults):
        for key in ["enable_nova", "nova_compute_virt_type"]:
            assert key in ciab_defaults, f"Missing default: {key}"
