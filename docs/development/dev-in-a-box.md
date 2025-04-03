# Dev-in-a-box

To deploy dev-in-a-box, use the following procedure:

Launch a baremetal instance, or a VM, with ubuntu 22.04 as the OS (As of 2023.1 release), and associate a floating IP.  Further steps will happen after SSH to said instance.



Install chi-in-a-box as usual

```
sudo apt-get update
sudo apt-get install \
    python3-venv \
    python3-dev

git clone https://github.com/chameleoncloud/chi-in-a-box
cd chi-in-a-box
git submodule update --init

./cc-ansible install_deps
./cc-ansible --site ../site-config init
```

Before editing the site-config, we'll create some "dummy" network interfaces, so that we don't depend on the external IP addressing or interface names.

```
# set up a bridge, it will be used as both internal and external api interface.
sudo ip link add br_fake type bridge
sudo ip addr add 172.16.200.10/24 dev br_fake
sudo ip link set br_fake up

# create a veth-pair, this will be used for the neutron network interface
sudo ip link add veth_na type veth peer veth_nb
sudo ip link set veth_na master br_fake
sudo ip link set veth_na up
sudo ip link set veth_nb up
```

Overwrite `defaults.yml`in your site-config to contain the following, which references the interface names and IPs above.

```
---
kolla_base_distro: ubuntu

network_interface: "br_fake"
kolla_internal_vip_address: "172.16.200.254"

neutron_networks:
- name: public
  bridge_name: br-ex
  external_interface: "veth_nb"
  cidr: 172.16.200.0/24
  gateway_ip: 172.16.200.1
  allocation_pools:
   - start: 172.16.200.30
     end: 172.16.200.40
     
# disable services to speed up dev deployment
enable_prometheus: false
enable_central_logging: false
```

Finally, finish the deploy.

```
./cc-ansible --site ../site-config bootstrap-servers
./cc-ansible --site ../site-config deploy

#TODO: this will fail partway through because we haven't defined sharednet1
# just ignore the failure if you don't need the things from post-deploy 
./cc-ansible --site ../site-config post-deploy
```



To access the site from your local machine, we recommend a tool like \`sshuttle\`, which can be installed locally, and invoked as:

```
sshuttle -r user@floatingip 172.16.200.254/32
```

while sshuttle is running, accessing that ip in your browser or via cli tools should work.

You can log into horizon using the username and password found in \`site-config/admin-openrc.sh\`, which post-deploy creates.
