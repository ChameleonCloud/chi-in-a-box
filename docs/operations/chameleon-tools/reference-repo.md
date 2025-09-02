# Reference Repo Generator

The Reference Repo Generator can be run at sites to update the Chameleon
reference repository with any new changes.

The Reference Repo Generator tool is bundled into the site tools Docker image.

A systemd timer is configured to run the tool once a week.

## Configuration and Execution

The site tools containing the Reference Repo Generator are installed onto the
`control` node in the site configuration Ansible inventory. The configuration
steps are included in the `post-deploy`. You can also manually configure and
run the tool by executing the `chameleon_reference_repo` playbook.

```sh
cc-ansible --playbook playbooks/chameleon_reference_repo.yml
```

The playbook will pull the latest chameleon_reference_repo Docker image to
run the tool.

## Required Environment Variables

To push changes to the GitHub reference repository (enabled by default), the
reference repo generator requires a valid `GITHUB_TOKEN` for authentication.

You must provide this token securely (do not commit it to the repository),
instead, you can pass it as an extra variable when running the playbook:

```sh
cc-ansible --playbook playbooks/chameleon_reference_repo.yml --extra "github_token=YOUR_GITHUB_TOKEN"
```

The token will be placed in the environment via the generated envvars file.
