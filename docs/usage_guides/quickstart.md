# quickstart


1. clone this repo, we use the path `/opt/chi-in-a-box` by convention.
   ```
   cd /opt
   git clone https://github.com/chameleoncloud/chi-in-a-box
   cd chi-in-a-box
   ```
1. install any missing dependencies
   ```
   apt-get install \
        python3 \
        python3-dev \
        python3-venv \
        jq
   ```
1. install the cc-ansible tooling and its own dependencies
   ```
   ./cc-ansible install_deps
   ```
1. template out a site-config directory. We'll use "/opt/site-config" by convention
   ```
   ./cc-ansible --site /opt/site-config init
   export CC_ANSIBLE_SITE=/opt/site-config
   ```
1. Identify which network interface you want the APIs to listen on, and a spare IP available in that subnet.
   ```
   $ ip -4 -br a
   lo               UNKNOWN        127.0.0.1/8
   eno33np0         UP             10.31.1.51/28 metric 100
   ```
   On our server, we would choose `eno33np0`, and select a second, known unused IP in the subnet `10.31.1.48/28`
1. Edit `/opt/site-config/defaults.yml` to contain a "minimum viable" config.
   ```
   ---
   kolla_base_distro: ubuntu
   network_interface: eno33np0
   kolla_internal_vip_address: 10.31.1.62

   # skip these services to speed up our first tests
   enable_prometheus: false
   enable_central_logging: false

   # tell neutron which interface to use for tenant networks
   neutron_networks:
     - name: physnet1
       bridge_name: br-physnet1
       external_interface: en34np1
   ```
1. bootstrap the controller node(s). This will install various tooling and prerequisites such as the docker runtime, modification of /etc/hosts, and installation of tools into an isolated virtualenv under /etc/ansible/venv
   ```
   ./cc-ansible bootstrap-servers
   ```
1. now that the tooling is installed, we can run some end-to-end prechecks
   ```
   ./cc-ansible prechecks
   ```
1. download up to date containers
   ```
   ./cc-ansible pull
   ```

1. Deploy all of the configured services
   ```
   ./cc-ansible deploy
   ```