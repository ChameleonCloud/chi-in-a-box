"""Integration tests: render genconfig for each profile, assert on output.

Two flavors:

  - *Smoke*: the pipeline runs end-to-end and produces the services we
    expect, with no unrendered Jinja.
  - *Content*: specific rendered values reflect what the profile asked
    for. Use GenconfigResult's `.services()`, `.ini()`, `.text()`
    helpers; don't parse rendered files by hand.

This file is short on purpose. As cherry-picks land KVM-specific
features, add per-feature assertions in their own classes — see the
examples below for shape.
"""


class TestMinimalSmoke:
    """Does site-config.example + _base render at all?"""

    def test_output_produced(self, minimal_config):
        assert minimal_config.services(), "genconfig produced no service dirs"

    def test_core_services_rendered(self, minimal_config):
        for svc in ["keystone", "horizon", "neutron-server", "nova-api"]:
            assert svc in minimal_config.services(), f"Missing service: {svc}"

    def test_no_unrendered_jinja(self, minimal_config):
        for conf in minimal_config.output_dir.rglob("*.conf"):
            assert "{{" not in conf.read_text(), (
                f"Unrendered Jinja in {conf.relative_to(minimal_config.output_dir)}"
            )


class TestKVMSmoke:
    """Does the KVM profile render at all?"""

    def test_output_produced(self, kvm_config):
        assert kvm_config.services()

    def test_no_unrendered_jinja(self, kvm_config):
        for conf in kvm_config.output_dir.rglob("*.conf"):
            assert "{{" not in conf.read_text(), (
                f"Unrendered Jinja in {conf.relative_to(kvm_config.output_dir)}"
            )


class TestKVMNova:
    """Example content assertions: KVM-specific nova scheduler filters."""

    def test_blazar_filter_present(self, kvm_config):
        filters = kvm_config.ini("nova-api", "nova.conf").get(
            "filter_scheduler", "enabled_filters"
        )
        assert "BlazarFilter" in filters

    def test_no_pci_filter_without_gpu(self, minimal_config):
        filters = minimal_config.ini("nova-api", "nova.conf").get(
            "filter_scheduler", "enabled_filters"
        )
        assert "PciPassthroughFilter" not in filters
