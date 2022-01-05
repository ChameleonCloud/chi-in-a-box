# Dataplane Switches

Currently CHI-in-a-Box has built-in support for a variety of physical switches, including:

* Cisco 300-series
* Corsa DP2000-series (**official support**)
* Dell OS9 (**official support**)
* Dell OS10 (**official support**)
* Juniper Junos

(**official support** denotes switches that are regularly tested by the Chameleon team)

A full list is available [here](https://docs.openstack.org/networking-generic-switch/latest/supported-devices.html). The network switches must be remotely manageable, typically with SSH (though some vendors have different interfaces, which should be supported if they are the primary interface.) For security, those interfaces should only be exposed on an internal network isolated from tenant networks controllable by users.

Switch login credentials will be templated out as plain text into several root-owned files on the CHI-in-a-Box management nodes responsible for orchestrating the network topology. The credentials themselves are encouraged to be stored encrypted in the `passwords.yml` file of your [site configuration](../../The-site-configuration/).

#### Not enough support?

These requirements are not set in stone; anything technically possible can be made a reality with some elbow grease and Python hacking. Let us know what you think.
