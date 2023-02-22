# How Deployment Works

Deploying a CHI-in-a-Box site proceeds as a sequence of steps. Most will only need to be completed once, but they can be repeated as needed in case of configuration changes.

Commands are executed using the `cc-ansible` executable in the CHI-in-a-box repository, and configuration done by editing text files. These commands and edits are done on the **Deploy Host**, in order to configure and manage the **Control Nodes**.  Most minimal installations will simply run the **Deploy Host**  on the same node as the CO

1. Download and install dependencies, and the CHI-in-a-Box tools on your **Deploy Host**
2. **`Initialize`** your **`Site-Configuration`**
3. Configure the network interfaces on your **`Control Nodes`**.
4. Add your **`Control Nodes` ** to the **ansible inventory** in your **site configuration,** and set any host variables needed to connect
5. Fill out your **defaults.yml** with all site-wide config values
6. **Bootstrap** the control nodes
7. **Deploy** services onto the control nodes
8. Run **Post-Deploy** which will use values from defaults.yml to pre-create various openstack objects with the (now running) API, as well as several periodic utility tasks.
9. Run manual steps using the OpenStack CLI, API, or scripts
