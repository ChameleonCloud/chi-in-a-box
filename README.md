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

You can test your playbooks using a Vagrant VM before you push it up. There is a convenient `make` target to run any playbook located in `playbooks/`:

```
# Tests playbooks/grafana.yml
make test-grafana
```

**Note**: If you are doing a lot with testing playbooks like this, you'll probably want to make sure your local directory is properly synced with the Vagrant VM. This often doesn't work properly out of the box. To ensure that your working directory is always properly synced, you can use `rsync-auto`:

```
vagrant rsync-auto
```
