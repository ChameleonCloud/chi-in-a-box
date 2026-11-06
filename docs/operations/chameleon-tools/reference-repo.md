# Reference Repo Generator

The Reference Repo Generator can be run at sites to update the Chameleon
reference repository with any new changes.

The Reference Repo Generator tool is bundled into the site tools Docker image.

A systemd timer is configured to run the tool once a month. The timer is off by
default. To turn it on, set `enable_chameleon_reference_repo: yes` in the site
`defaults.yml`. To change the schedule, set `chameleon_reference_repo_calendar`
to a systemd calendar expression, such as `"*-*-01,15 06:00"`.

To run the tool now and read its output:

```shell
systemctl start chameleon-reference-repo.service
journalctl -u chameleon-reference-repo.service
```

## Configuration and Execution

The site tools containing the Reference Repo Generator are installed onto the
`control` node in the site configuration Ansible inventory. The configuration
steps are included in the `post-deploy`. You can also manually configure and
run the tool by executing the `chameleon_reference_repo` playbook.

```shell
cc-ansible --playbook playbooks/chameleon_reference_repo.yml
```

The playbook pulls the site tools image at the version set by
`chameleon_site_tools_tag`. See [Chameleon tools](README.md) for how to update it.

## Required Environment Variables

To push changes to the GitHub reference repository (enabled by default), the
reference repo generator requires a valid `GITHUB_TOKEN` for authentication.

You must provide this token securely (do not commit it to the repository).
Add it to the site passwords as `github_token`:

```shell
cc-ansible edit_passwords
```

The token will be placed in the environment via the generated reference-repo.env file.
