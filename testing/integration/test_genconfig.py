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
