On Chameleon, users are allowed to provision bare metal machines and are granted root access to the entire machine. This grants users a tremendous amount of power. While we expect Chameleon users to behave responsibly, hosts can still be compromised via a variety of circumstances. Most of our security considerations are focused on preventing a host compromise from affecting other users of the system, and the health of the system itself.

## Network security
- Care must be taken to isolate the IPMI/BMC interfaces from the host OS. The BMC network interface should be isolated on a separate VLAN segment that is plumbed only to the control nodes (the ones running OpenStack.) 
- If Floating IPs are to be used, some form of external firewall or intrusion detection system is advised. Cybersecurity personnel at the hosting institution should be aware of the nature of the activity on the subnet used for provisioning bare metal machines, as it can be bizarre (in the case of networking experiments) or malicious (in the case of a host compromise via trivial brute-force.)
- The control nodes should be logically isolated from the nodes being provisioned by users via VLAN segments. Both the control nodes and the provisioned nodes should additionally be isolated from the rest of the host institution network via similar means.

## Host security
- BIOS passwords should be set to disallow trivial modification of important settings related to PXE booting and otherwise. The BMC password should be set to a non-default value. 
