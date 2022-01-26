# Security considerations

On Chameleon, users are allowed to provision bare metal machines and are granted root access to the entire machine. This grants users a tremendous amount of power. While we expect Chameleon users to behave responsibly, hosts can still be compromised via a variety of circumstances. Most of our security considerations are focused on preventing a host compromise from affecting other users of the system, and the health of the system itself.

### Network security

* Care must be taken to isolate the IPMI/BMC interfaces from the host OS. The BMC network interface should be isolated on a separate VLAN segment that is plumbed only to the control nodes (the ones running OpenStack.)
* If Floating IPs are to be used, some form of external firewall or intrusion detection system is advised. Cybersecurity personnel at the hosting institution should be aware of the nature of the activity on the subnet used for provisioning bare metal machines, as it can be bizarre (in the case of networking experiments) or malicious (in the case of a host compromise via trivial brute-force.)
* The control nodes should be logically isolated from the nodes being provisioned by users via VLAN segments. Both the control nodes and the provisioned nodes should additionally be isolated from the rest of the host institution network via similar means.

### Host security

* BIOS passwords should be set to disallow trivial modification of important settings related to PXE booting and otherwise. The BMC password should be set to a non-default value.

### Network Isolation and Security Policies

* The site only needs access to the public internet, and users will be running untrusted code on the baremetal compute nodes. Please make sure that the nodes cannot access any sensitive internal networks.
* The controller node is only accessed by whoever is following this quickstart, or users that they authorize. While normal users access the web interface, they do not have access to the system configuration.
* While Chameleon users must be sponsored by an approved project, they might not be US citizens. Please make sure that your security policies permit this.
* The floating-ips used by nodes and router interfaces may be sending arbitrary traffic, opening common ports, or other tasks that commonly trigger network security alerts. While our policies forbid malicious action, many common research use-cases can mimic this. Therefore, please ensure that your network ACLs have a "permit-all" rule applied to the floating-ip range, and that you have an arrangement with your network team on how to handle abuse and alerts.
