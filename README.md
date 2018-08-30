# ansible-playbooks

Ansible playbooks for deploying Chameleon operations systems

## Development setup

This requires Vagrant and Virtualbox (with guest additions) if you want to test playbooks locally.

**Mac OS X**

Can be installed easily using Homebrew.

```bash
brew cask install vagrant
brew cask install virtualbox
# Install guest additions for Virtualbox, needed for file syncing
vagrant install vagrant-vbguest
```

### Testing playbooks locally

You can test your playbooks using a Vagrant VM before you push it up. There is a convenient `make` target to run any playbook located in [`playbooks/`](./playbooks):

```bash
# Tests playbooks/grafana.yml
make grafana-test
```

Each playbook is run in _its own Vagrant VM_. This means you will have many VMs running if you are testing multiple playbooks.

**Note**: If you are doing a lot with testing playbooks like this, you'll probably want to make sure your local directory is properly synced with the Vagrant VM. This often doesn't work properly out of the box. To ensure that your working directory is always properly synced, you can run a "watch" task in a separate tab:

```bash
# Automatically syncs working directory to test VM.
# (example is for grafana playbook VM)
make grafana-watch
```

Sometimes you may want to see what's going on inside the VM. You can launch a shell into the VM using a different `make` target.

```bash
# SSH into the test VM. (Requires that a prior 'test' run has already happened.)
make grafana-shell
```

If you want to tear down the VM, you can run the `clean` target:

```bash
# Wipe the test VM.
make grafana-clean
```

## Deployment

Each Chameleon site is deployed separately. This allows each site to customize the deploy to their specific concerns. Each site is represented via an inventory located in [`inventories/`](./inventories). Inventories are the primary way that the behavior of the generic playbooks is customized.

### Deployment node setup

To set up a virtualenv and install the Ansible python module(s), first run the `setup` make task:

```bash
make setup
```

This should also prompt you to create a new site inventory (see next section "Creating a new site inventory" for what exactly this means.) If you have done that, then the next step is to provision the Ansible deploy node (which should be localhost, effectively) with Ansible. It's Ansible all the way down! This will install any other python modules and packages which are necessary for the operation of the Ansible tasks. It's the expectation that as new modules are introduced to this repo, their dependencies are properly bootstrapped by the `ansible` role.

```bash
./ansible-playbook playbooks/ansible.yml
```

### Creating a new site inventory

To create a new site inventory (probably won't happen very often, only when deploying a new site), you need to initialize a few things, like an Ansible Vault password, and an inventory directory. This can be done for you by running the `./ansible-inventory` script.

```bash
./ansible-inventory
# Output:
# Enter the name of the inventory: chi_some_site_name
# Creating inventory directory structure:
#   - ./inventories/chi_some_site_name
# Creating initial hosts file:
#   - ./inventories/chi_some_site_name/hosts
# Creating initial vault password in ./vault_password
# Your new inventory environment is now set up.
```

### Applying playbooks

Playbooks are set up to target a host group with the same name. This means the `grafana` playbook will target the `grafana` host group etc. To run a playbook, you can use the `./ansible-playbook` wrapper script, which just sets up two important parameters for you: the Ansible Vault configuration, and the inventory path. This requires you have already done the setup using `./ansible-inventory`.

```bash
# Run the 'grafana' playbook (deploys/updates grafana)
./ansible-playbook playbooks/grafana.yml
# Run only the tasks tagged 'configuration' in the 'grafana' playbook
# (Any arguments normally passed to ansible-playbook can be passed here.)
./ansible-playbook --tags configuration playbooks/grafana.yml
```

## Configuration secrets

Secrets like database and user passwords or sensitive API keys should be encrypted with [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). Once a deploy node is set up, there should be a Vault password generated in a file called `vault_password` in the Ansible working directory. This is used as a symmetrical cipher key to encrypt and decrypt secrets. This key should **never be stored in source control.** To encrypt a secret, you can use the `./ansible-vault` wrapper script, which sets up the Vault configuration for you. Using the `encrypt_string` command, you can generate valid YAML that you can then paste wherever necessary in your variable or task definitions.

```bash
# Create new variable named 'my_variable_name'. This will output valid YAML
# setting that variable to a value that will be decrypted by Ansible at runtime.
echo "my variable value" | ./ansible-vault encrypt_string --stdin-name="my_variable_name"
```

