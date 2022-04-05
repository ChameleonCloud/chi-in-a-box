# Resource Reservation

## Overview

### Requirements

## Adding Resources

### Hosts

### Devices

### Networks

Add a network extra capability:

```
openstack reservation network set --extra key=value NETWORK_ID
```

### Floating IPs

Create a new reservable floating IP

```
openstack reservation floatingip create <NETWORK_ID> <FLOATING_IP_ADDRESS>
```
