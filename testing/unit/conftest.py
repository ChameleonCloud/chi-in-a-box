"""Fixtures for unit tests. No ansible or kolla-ansible needed."""

import subprocess
import yaml
import pytest


@pytest.fixture
def yq_merge(tmp_path, ciab_defaults_path):
    """Returns a function that merges overrides onto chi-in-a-box defaults via yq."""
    def _merge(overrides):
        override_file = tmp_path / "overrides.yml"
        override_file.write_text(yaml.dump(overrides))
        result = subprocess.run(
            ["yq", "eval-all", ". as $item ireduce ({}; . * $item)",
             str(ciab_defaults_path), str(override_file)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            pytest.skip(f"yq not available: {result.stderr}")
        return yaml.safe_load(result.stdout)
    return _merge
