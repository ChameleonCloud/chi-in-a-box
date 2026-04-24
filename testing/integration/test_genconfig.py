"""Smoke tests for `cc-ansible genconfig` end-to-end.

A failure here means rendered service config would fail on a real host.
Rendered output is preserved at testing/output/_base/ for inspection.
"""


def test_genconfig_produces_output(genconfig_output):
    assert any(genconfig_output.iterdir()), "genconfig produced no service dirs"


def test_core_services_rendered(genconfig_output):
    services = {d.name for d in genconfig_output.iterdir() if d.is_dir()}
    for svc in ["keystone", "horizon", "neutron-server", "nova-api"]:
        assert svc in services, f"Missing service directory: {svc}"


def test_no_unrendered_jinja(genconfig_output):
    for conf in genconfig_output.rglob("*.conf"):
        text = conf.read_text()
        assert "{{" not in text, (
            f"Unrendered Jinja in {conf.relative_to(genconfig_output)}"
        )
