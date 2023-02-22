# CC-Ansible

## CC-Ansible

The `cc-ansible` script in the root of the repo is used to drive the deployment. With this tool you can upgrade parts of the system, reconfigure various services, update and edit encrypted passwords, and run Chameleon-specific Ansible playbooks to set up supporting infrastructure not provided by the Kolla-Ansible project (such as Chameleon's automated [hammers](https://github.com/chameleoncloud/hammers) toolkit).

#### Specifying the site configuration

Most commands require specifying a path to the _site configuration_, which contains your site-specific variables, overrides, and configuration. You can specify this in two ways, either with the `--site` flag, or by setting the env variable `CC_ANSIBLE_SITE`.

```bash
./cc-ansible --site /path/to/site-config <cmd>
# Or, by setting env
export CC_ANSIBLE_SITE=/path/to/site-config
./cc-ansible <cmd>
```

#### Applying playbooks

Playbooks are set up to target a host group with the same name. This means the `grafana` playbook will target the `grafana` host group etc. To run a playbook, you can use the `./cc-ansible` wrapper script, which just sets up two important parameters for you: the Ansible Vault configuration, and the inventory path.

```bash
# Run the 'grafana' playbook (deploys/updates grafana)
./cc-ansible --playbook playbooks/grafana.yml
# Run only the tasks tagged 'configuration' in the 'grafana' playbook
# (Any arguments normally passed to ansible-playbook can be passed here.)
./cc-ansible --playbook playbooks/grafana.yml --tags configuration
```

#### Running Kolla-Ansible actions

Much of the deployment is ultimately controlled by [Kolla-Ansible](https://docs.openstack.org/kolla-ansible/latest/). To invoke, you can use the `./cc-ansible` tool much like you could use `kolla-ansible`:

```bash
# Deploy the Neutron components
./cc-ansible deploy --tags neutron
# Pull latest images for all components
./cc-ansible pull
# Upgrade Nova and Ironic
./cc-ansible upgrade --tags nova,ironic
```

#### Post-deployment

There is a `post-deploy` script you can run to finish things up. This will install compatible versions of all OpenStack clients for your deployment and set up some OpenStack entities needed to do bare metal provisioning.

```bash
./cc-ansible post-deploy
```

Finally, consider adding the following to your .bashrc or similar:

```bash
# Pre-set site so you don't have to type it each time
export CC_ANSIBLE_SITE=/opt/config/<your_site>

# Source OpenStack client environment automatically
if [ -f "$CC_ANSIBLE_SITE/admin-openrc.sh" ]; then
  source "$CC_ANSIBLE_SITE/admin-openrc.sh"
fi

# Source virtualenv to have access to OpenStack clients installed
# in virtualenv (assumes this repo is installed at /etc/ansible)
if [ -f /etc/ansible/venv/bin/activate ]; then
  export VIRTUAL_ENV_DISABLE_PROMPT=1
  source /etc/ansible/venv/bin/activate
fi
```

### Configuration secrets

Secrets like database and user passwords or sensitive API keys should be encrypted with [Ansible Vault](https://docs.ansible.com/ansible/latest/user\_guide/vault.html) in a `passwords.yml` file located in the site configuration. This is encrypted with a symmetrical cipher key (`vault_password`). This key should **never be stored in source control**. You can edit or view the encrypted contents with the `./cc-ansible` tool:

```bash
# Opens an interactive editor for editing passwords
./cc-ansible edit_passwords
# Prints unencrypted passwords to stdout
./cc-ansible decrypt_passwords
```

## Common tasks

### Upgrade to a new version of an OpenStack image/config

A full upgrade of a given service (or set of services) is a `pull` operation followed by an `upgrade`. The `pull` will pull the latest version of the Docker image for the service(s) and can be done ahead of time to save time in the maintenance window, if desired. The `upgrade` task will perform any database migrations, update the runtime configuration, and redeploy the service at the new version.

```shell
./cc-ansible pull --tags ironic
./cc-ansible upgrade --tags ironic
# Or, perform a full (!) upgrade of all OpenStack services
./cc-ansible pull && ./cc-ansible upgrade
```
