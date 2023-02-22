# The site configuration

Every CHI-in-a-Box deployment is highly configurable, though many settings are defaulted to what Chameleon considers the most useful or likely scenario. Some configuration values like hostnames or private IP addresses do not have defaults and must be specified by the operator. These settings are specified as part of a _site configuration_, which is a folder containing a few important files:

## Summary

* an [Ansible inventory](https://docs.ansible.com/ansible/latest/user\_guide/intro\_inventory.html)
* an [Ansible Vault](https://docs.ansible.com/ansible/latest/user\_guide/vault.html) password file
* an (encrypted) [passwords](https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html#kolla-passwords) YAML file
* a `defaults.yaml` file used to configure most settings. These defaults apply in a low-priority and can be overridden via Ansible inventory host\_vars or group\_vars.
* an (optional) post-deploy YAML file, which is an Ansible playbook that can be run after normal post-deploy steps via `cc-ansible post-deploy`. This is a useful place to put additional settings that need to be invoked via Ansible, such as setting up tagged VLAN interfaces or custom firewall rules.

A directory with examples is located in the CHI-in-a-Box repo at `./site-config.example`

{% embed url="https://github.com/ChameleonCloud/chi-in-a-box/tree/stable/xena/site-config.example" %}
