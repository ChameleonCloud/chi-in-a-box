"""Integration tests: render genconfig for each profile, spot-check output.

Tests parametrize over PROFILES in conftest.py (baremetal, kvm, ...).
Each test runs once per profile. Rendered output is preserved at
testing/output/<profile>/ for manual comparison against real site-configs.

Run via Docker for isolation:
    docker build -f testing/Dockerfile -t chi-in-a-box:test .
    docker run --rm chi-in-a-box:test pytest
"""


def test_genconfig_succeeds(profile_config):
    assert profile_config.output_dir.exists()


def test_key_services_rendered(profile_config):
    # Services common to any OpenStack site. Per-profile expected/
    # forbidden sets (e.g. ironic-conductor for baremetal but not kvm)
    # can move into a declarative config if/when invariant assertions
    # justify it — we're in discovery mode for now.
    services = profile_config.services()
    for svc in ["keystone", "horizon", "neutron-server", "nova-api"]:
        assert svc in services, f"Missing service: {svc}"


def test_no_raw_jinja2_in_configs(profile_config):
    for conf_file in profile_config.output_dir.rglob("*.conf"):
        content = conf_file.read_text()
        assert "{{" not in content, (
            f"Unrendered Jinja2 in {conf_file.relative_to(profile_config.output_dir)}"
        )
