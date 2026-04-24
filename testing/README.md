# chi-in-a-box test harness

End-to-end tests for `cc-ansible genconfig`. Run in CI on every PR, and
locally.

## Running
First, ensure `cc-ansible install_deps` has been run.

    pytest testing/unit/           # fast, no genconfig
    pytest testing/integration/    # runs genconfig per profile (~1m each)

Or in the CI-equivalent container:

    docker build -t ciab:test .
    docker run --rm ciab:test pytest testing/

Rendered config from integration runs is preserved at
`testing/output/<profile>/` locally, and uploaded as the
`genconfig-output` artifact in CI.

## Profiles are site-config fragments

Profiles contain site-config fragments under `testing/profiles/<name>/`:

    defaults.yml     # variable overrides (optional)
    inventory/       # inventory overrides (optional, merged by ansible)

The test harness assembles a full site-config by layering:

    site-config.example   +   _base fragment   +   named profile   =   assembled site-config

From there it's the usual cc-ansible deploy flow: `kolla/defaults.yml` is
merged with the assembled site-config's `defaults.yml` via yq, producing
`globals.yml`, which kolla-ansible reads.

## Adding a profile

1. `testing/profiles/<name>/defaults.yml` — variable overrides layered on
   `_base`.
2. (optional) `testing/profiles/<name>/inventory/<anything>` — any file
   here is merged with the base inventory via ansible's
   inventory-directory behavior. A small override (e.g. populating
   `[compute]`) doesn't need to copy the full `hosts` file.
3. A session-scoped fixture in `testing/integration/conftest.py`:

       @pytest.fixture(scope="session")
       def mysite_config(tmp_path_factory):
           return _run_genconfig(
               tmp_path_factory.mktemp("mysite"),
               [BASE_PROFILE_DIR, PROFILES_DIR / "mysite"],
               preserve_name="mysite",
           )

4. Tests take `mysite_config` as a parameter.

## Pytest idioms this suite uses

- **`@pytest.fixture(scope="session")`** — the function runs once per pytest 
  invocation and its return value is cached. Each profile renders once and many
  tests share the output.
- **Fixture injection** — a test's parameter name (e.g. `kvm_config`)
  tells pytest which fixture to call and inject, but it's not called directly.
- **`tmp_path_factory`** is a pytest-provided fixture handing out
  unique temp dirs.
