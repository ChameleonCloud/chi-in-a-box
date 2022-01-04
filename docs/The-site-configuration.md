Every CHI-in-a-Box deployment is highly configurable, though many settings are defaulted to what Chameleon considers the most useful or likely scenario. Some configuration values like hostnames or private IP addresses do not have defaults and must be specified by the operator. These settings are specified as part of a _site configuration_, which is a folder containing a few important files:

## Required Configuration
- an [Ansible inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- an [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) password file
- an (encrypted) [passwords](https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html#kolla-passwords) YAML file
- a `defaults.yaml` file used to configure most settings. These defaults apply in a low-priority and can be overridden via Ansible inventory host_vars or group_vars.
- an (optional) post-deploy YAML file, which is an Ansible playbook that can be run after normal post-deploy steps via `cc-ansible post-deploy`. This is a useful place to put additional settings that need to be invoked via Ansible, such as setting up tagged VLAN interfaces or custom firewall rules.

An example configuration is located in the CHI-in-a-Box repo at `./site-config.example`.

## Optional Configuration
### Chameleon Identity Federation
#### What is Identity Federation?

Federated identity allows a user to link existing identities and attributes across multiple distinct systems. In practice, this allows an operator to configure a system to allow access to users from other systems. Chameleon Identity Federation allows existing Chameleon users access to the configured associate site. This allows the site operator to leverage all of the infrastructure that the Chameleon project has built for handling user, project, and allocation management through the [Chameleon Portal](https://chameleoncloud.org).

#### Enabling Chameleon Identity Federation
Before an associate site can enable federation, that site must obtain a client identifier from Chameleon administrators.

- Open a ticket in the [help desk](https://www.chameleoncloud.org/user/help/) explaining some details of the site institution and hardware. Chameleon staff will issue a Client ID for the site, which will need to be entered into the site configuration.
- The Client ID is configured in `globals.yml` as keystone_idp_client_id. To satisfy requirements of the deployment tool, the encrypted passwords file should set keystone_idp_client_secret should to "public".
- Use `reconfigure` to apply the changes and generate a new keystone domain called "chameleon". At this point, federated login should now be available on the site.
- Add the "admin" role an operator user.
  - Find and take note of the desired user and group UUIDs. Be sure to query the user and project entities in the "chameleon" domain.

        openstack user show --domain chameleon <username>

        openstack project show --domain chameleon openstack

  - Make the role assignment

        openstack role add --user <user_uuid> --project <project_uudi> admin

## Prometheus-IPMI-Exporter

We've added the ability to export metrics from the IPMI interface of your systems. This uses the existing prometheus-ipmi-exporter project.
For now, the configuration is somewhat manual, and will be more integrated in the future.

Example defaults.yml snippet:
```
prometheus_ipmi_exporter_modules:
  - name: default
    user: <IPMI_USER>
    password: <IPMI_PASSWORD>
    collectors:
      - bmc
      - ipmi
      - chassis
    endpoints:
      - <node1_bmc_ip_address>
      - <node2_bmc_ip_address>
      - ...
```