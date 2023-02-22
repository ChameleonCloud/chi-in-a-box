# Assumed Knowledge

Deploying and Operating a CHI-in-a-Box site will be challenging without familiarity with the following concepts.

#### Linux systems

In particular, using a shell, privilege escalation, user and group management, linux networking, and mounts and filesystems. Specific linux networking knowledge includes network namespaces and virtual ethernet devices (veths)

#### Basic network administration

You'll need to know about vlans, and how to log into a switch using SSH and use its commandline for configuration, in particular configuring vlan trunks and access ports. While the concepts are fairly universal, the specifics will depend on the manufacturer and model for your switches.

#### Ansible

CHI-in-a-box leverages the Ansible and Kolla-Ansible projects, so basic familiarity will be very helpful. In particular, what an Ansible "Inventory" is, how to use host and group variables, and how to invoke a playbook and read the output.

* [Ansible Inventory Basics](https://docs.ansible.com/ansible/latest/inventory\_guide/intro\_inventory.html#inventory-basics-formats-hosts-and-groups)
* [Host and Group Variables](https://docs.ansible.com/ansible/latest/inventory\_guide/intro\_inventory.html#organizing-host-and-group-variables)
* [Ansible CLI Reference](https://docs.ansible.com/ansible/latest/command\_guide/index.html#command-guide-index)
* [Using Ansible Playbooks](https://docs.ansible.com/ansible/latest/playbook\_guide/index.html#playbook-guide-index)

#### Docker

Only basic knowledge is needed, as all CHI-in-a-Box services are deployed in Docker containers. On occasion, inspecting the environment inside a container or volume can be helpful for debugging purposes. See [Docker's getting started guide](https://docs.docker.com/get-started/) for more detail.

#### OpenStack

This is a deep well, and where we've placed the most effort in abstracting the most complex parts.

You will need to install and use the OpenStack CLI tools, and broadly know which services to look at when things go wrong, e.g. reading the logs, listing user instances or networks, and so on.

CHI-in-a-Box leverages Kolla-Ansible to generate configurations for each enabled OpenStack service, and then to deploy said services. In the case of issues or failures during deployment itself, [you may find their deployment guide a helpful reference](https://docs.openstack.org/project-deploy-guide/kolla-ansible/xena/).

For issues, or available options for a particular service, e.g. Identity, Image storage, or Networking, see OpenStack's documentation for each service.

* [Installation guides, per-service](https://docs.openstack.org/xena/install/)
* [Configuration and Administration Guides, per-service](https://docs.openstack.org/xena/admin/)

