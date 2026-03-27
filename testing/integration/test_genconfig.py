"""Integration tests: run genconfig and assert on rendered config.

These tests require cc-ansible install_deps to have been run.
All output is sandboxed to pytest tmpdirs.

Run via Docker for isolation:
    docker build -f testing/Dockerfile -t ciab-test .
    docker run ciab-test testing/integration/ -v
"""

class TestMinimalProfile:
    """Bare minimum config renders without errors."""

    def test_genconfig_succeeds(self, minimal_config):
        assert minimal_config.output_dir.exists()

    def test_key_services_rendered(self, minimal_config):
        services = minimal_config.services()
        for svc in ["keystone", "horizon", "neutron-server", "nova-api"]:
            assert svc in services, f"Missing service: {svc}"

    def test_no_raw_jinja2_in_configs(self, minimal_config):
        for conf_file in minimal_config.output_dir.rglob("*.conf"):
            content = conf_file.read_text()
            assert "{{" not in content, (
                f"Unrendered Jinja2 in {conf_file.relative_to(minimal_config.output_dir)}"
            )


class TestKVMBlazar:
    """Blazar config for KVM sites with flavor reservation."""

    def test_flavor_plugin_present(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        plugins = conf.get("manager", "plugins")
        assert "flavor.instance.plugin" in plugins

    def test_flavor_plugin_absent_by_default(self, minimal_config):
        conf = minimal_config.ini("blazar-manager", "blazar.conf")
        plugins = conf.get("manager", "plugins")
        assert "flavor.instance.plugin" not in plugins

    def test_flavor_instance_section_exists(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        assert conf.has_section("flavor:instance")

    def test_flavor_trait_rendered(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        trait = conf.get("flavor:instance", "placement_reservation_permitted_trait")
        assert "CUSTOM_TEST_TRAIT" in trait

    def test_physical_host_section_exists_without_ironic(self, kvm_config):
        """physical:host should render even when enable_ironic=false."""
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        assert conf.has_section("physical:host")

    def test_host_reservation_disabled(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        assert conf.get("physical:host", "allow_reservation") == "False"

    def test_filter_vm_hosts(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        assert conf.get("physical:host", "filter_vm_hosts") == "True"

    def test_allocation_enforcement(self, kvm_config):
        conf = kvm_config.ini("blazar-manager", "blazar.conf")
        filters = conf.get("enforcement", "enabled_filters")
        assert "ExternalServiceFilter" in filters


class TestKVMNova:
    """Nova config for KVM sites."""

    def test_blazar_filter_present(self, kvm_config):
        conf = kvm_config.ini("nova-api", "nova.conf")
        filters = conf.get("filter_scheduler", "enabled_filters")
        assert "BlazarFilter" in filters

    def test_pci_filter_when_gpu(self, kvm_gpu_config):
        conf = kvm_gpu_config.ini("nova-api", "nova.conf")
        filters = conf.get("filter_scheduler", "enabled_filters")
        assert "PciPassthroughFilter" in filters

    def test_no_pci_filter_without_gpu(self, kvm_config):
        conf = kvm_config.ini("nova-api", "nova.conf")
        filters = conf.get("filter_scheduler", "enabled_filters")
        assert "PciPassthroughFilter" not in filters

    def test_pci_device_spec_rendered(self, kvm_gpu_config):
        conf = kvm_gpu_config.ini("nova-api", "nova.conf")
        assert conf.has_option("pci", "device_spec")
        assert "10de" in conf.get("pci", "device_spec")


class TestKVMHorizon:
    """Horizon config for KVM sites with flavor reservation."""

    def test_flavor_reservation_ui(self, kvm_config):
        content = kvm_config.text("horizon", "custom_local_settings")
        assert "OPENSTACK_BLAZAR_FLAVOR_RESERVATION" in content

    def test_not_baremetal_only(self, kvm_config):
        content = kvm_config.text("horizon", "custom_local_settings")
        assert "CHAMELEON_BAREMETAL_ONLY = False" in content

    def test_baremetal_only_by_default(self, minimal_config):
        content = minimal_config.text("horizon", "custom_local_settings")
        assert "CHAMELEON_BAREMETAL_ONLY = True" in content

    def test_show_only_reserved_flavors(self, kvm_config):
        content = kvm_config.text("horizon", "custom_local_settings")
        assert "OPENSTACK_SHOW_ONLY_RESERVED_FLAVORS" in content

    def test_host_reservation_disabled_in_ui(self, kvm_config):
        content = kvm_config.text("horizon", "custom_local_settings")
        assert "'enabled': False" in content or '"enabled": False' in content
