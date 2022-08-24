---
description: Bringing up a minimal site to kick the tires
---

# Evaluation Site

## Introduction

A production site has many requirements and moving parts that make it difficult to understand. This guide will bring up a minimal site on a single node, and demonstrate how a production site extends these concepts.

## Requirements

Install **Ubuntu 20.04** on either a physical machine, or a VM.

This system will need the following requirements for a minimal test environment:

* One network interface that will serve both the public and internal APIs, as well as admin SSH access.
  * A hostname + IP address for this interface, e.g. `dev01 -> 10.100.0.10/24`
  * A hostname + reserved (not associated!) IP address for the HAProxy VIP, e.g.  `chi.dev -> 10.100.0.254/32`
* 20GB of disk space
* 8GB of ram
* 4 cpu cores

**To test TLS and/or identity federation, you will need to add:**

* A second network interface to separate the Public API from the internal/admin APIs
  * 2 Publicly routable IP addresses. As above, one bound to the interface, and one reserved for the HAProxy VIP.
  * A hostname and DNS record for the Public VIP
  * A TLS cert for this hostname

**To test VM support, you will need to add:**

* A third network interface to provide connectivity for guest instances: `neutron external interface`
* 40GB of disk space
* Additional RAM and cores as necessary.

**To Test baremetal support, you will need to add:**

* A baremetal node, with PXE boot support, and IPMI enabled.
* An interface, or a vlan or route on the internal API interface, that can communicate with the IPMI interface on the baremetal node.
* The in-band interface on the baremetal node must be on the same vlan as the `neutron external interface`.





