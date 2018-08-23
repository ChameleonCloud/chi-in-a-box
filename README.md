# ansible-playbooks

Ansible playbooks for deploying Chameleon operations systems

## Development setup

This requires Vagrant and Virtualbox (with guest additions) if you want to test playbooks locally.

**Mac OS X**
```
brew cask install vagrant
brew cask install virtualbox
# Install guest additions for Virtualbox, needed for file syncing
vagrant install vagrant-vbguest
```

### Testing playbooks locally

You can test your playbooks using a Vagrant VM before you push it up. There is a convenient `make` target to run any playbook located in [`playbooks/`](./playbooks):

```
# Tests playbooks/grafana.yml
make grafana-test
```

Each playbook is run in _its own Vagrant VM_. This means you will have many VMs running if you are testing multiple playbooks.

**Note**: If you are doing a lot with testing playbooks like this, you'll probably want to make sure your local directory is properly synced with the Vagrant VM. This often doesn't work properly out of the box. To ensure that your working directory is always properly synced, you can run a "watch" task in a separate tab:

```
# Automatically syncs working directory to test VM.
# (example is for grafana playbook VM)
make grafana-watch
```

## Region inventories

These playbooks are generic enough to be applied against multiple regions (sites). Each region is defined using an inventory file located in [`inventories/`](./inventories)
