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

Note: which versions tested?
