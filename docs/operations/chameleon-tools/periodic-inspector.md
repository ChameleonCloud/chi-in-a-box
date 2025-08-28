# Periodic Inspector

The periodic inspector can be run at sites to inspect the hardware
characteristics of individual nodes.

The periodic inspector tool is bundled into the site tools Docker
image.

A systemd timer is configured to run the inspector once a day.

## Configuration and Execution

The site tools containing the periodic inspector are installed onto the
`control` node in the site configuration Ansible inventory. The configuration
steps are included in the `post-deploy`. You can also manually configure and
run the image tools by executing the `chameleon_periodic_inspector` playbook.

```shell
cc-ansible --playbook playbooks/chameleon_periodic_inspector.yml
```

The playbook will pull the latest `chameleon_periodic_inspector` Docker image
to run the tool.
