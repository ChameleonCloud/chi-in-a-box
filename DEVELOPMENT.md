# Development guide

## Vagrant

### Install Vagrant and Virtualbox

```shell
brew cask install vagrant
brew cask install virtualbox
```

```shell
vagrant plugin install vagrant-hostmanager
vagrant plugin install vagrant-vbguest
```

If you are upgrading an existing installation, the following commands may be useful to ensure everything is up-to-date:

```shell
brew cask update vagrant
brew cask update virtualbox
vagrant plugin update
vagrant box update
```

### Add NAT network

A NAT network is used to simulate the "public" network in the CHI-in-a-Box installation.

```shell
VBoxManage natnetwork add -t OSNetwork -n "172.16.10.0/24" -e -h on
```

### Create Vagrant environment

The Vagrant environment is managed in the [`./vagrant`](./vagrant) directory.
You should use the wrapper-script provided in that directory to access Vagrant, as it sets up some things for you and accounts for Virtualbox-specific things such as the persistence of a default DHCP server that conflicts with the one required for the CHI-in-a-Box environment.

```shell
cd vagrant
./vagrant up
# To SSH to the provisioned server:
./vagrant ssh
```

**Note**: when working in the Vagrant VM, be careful of what you delete! The host checkout of `chi-in-a-box` is mounted inside the virtual machine, so if it is deleted, you may be losing work-in-progress.

## Using prebuilt image

- Need to update /etc/hosts
- Need to replace some other host entries
