---
description: A list of operations you can test to ensure your site is in working order.
---

# Verification Checklist

The following verification checklist are _user operations_ that should work. This is not an exhaustive list of what services should be running, how they should be configured, or other technical details. It only describes what functionality should be provided to the user, so you can verify operations.

### General verification

* [ ] Load the Horizon GUI homepage over HTTPS
* [ ] _If using federated identity_, ensure login with federated (e.g., Globus) credentials is possible
  * [ ] Logged-in users should see the list of all projects w/ active allocations in the top menu dropdown.
* [ ] _If not using federated identity_, ensure accounts are created for any users who will use the system. Users provisioned manually on the cluster should be able to log in with username/password.
* [ ] Ensure that admins have access to a special "openstack" project in the dropdown, which, when active in the GUI session, unlocks an additional Admin menu.
* [ ] Navigate to the Images view in the GUI and ensure there are some images for users to leverage.
* [ ] Navigate to the Compute -> Key Pairs section and add a Key Pair, if you have not done so already.
* [ ] Navigate to the API Access menu and download an Open RC file. Try to use this file to authenticate with the OpenStack CLI and obtain a token with `openstack token issue`. It should return a token.

### Bare-metal-specific

* [ ] _If using reservations_, navigate to the Leases view in the GUI and go to the calendar. Ensure that all nodes you have enrolled into the system are visible here (and not grayed out.)
  * [ ] Create a test lease for one of the nodes and ensure it transitions to ACTIVE state.
* [ ] Navigate to the Compute view and launch a test instance. Ensure the "baremetal" flavor is available and there is at least one network ("sharednet") in the available networks list.
  * [ ] _If using reservations_, pick the test reservation you created in the previous step.
  * [ ] Wait for the instance to provision successfully; it can take upwards of 15 minutes but will time out after 30 minutes (usually indicating boot error or network misconfig).
* [ ] Navigate to the Network -> Floating IP view and allocate a Floating IP if none exists.
  * [ ] Proceed to attach the Floating IP to your test instance.
* [ ] Once the instance transitions to the ACTIVE state, SSH to it as the "cc" user via its Floating IP, using the private key associated with the Key Pair you set up.

{% hint style="info" %}
For bare metal instances, it can take a few minutes after it has transitioned to ACTIVE state for SSH to become available. This is because Ironic will flip the instance to this state when it has started its final boot. Bare metal boots can take significant time, and then there is the time for DHCP/SSH to come up.
{% endhint %}

### KVM-specific

* [ ] Ensure there are flavors registered in the Admin -> Compute -> Flavors menu section.
* [ ] Navigate to the Network -> Security Groups view and create a new security group called "Allow SSH" that allows ingress on port 22.
* [ ] Navigate to the Compute view and launch a test instance. Ensure one of the registered flavors is selected and there is at least one network ("sharednet") in the available network list.
  * [ ] Wait for the instance to provision successfully.
* [ ] Navigate to the Network -> Floating IP view and allocate a Floating IP if none exists.
  * [ ] Proceed to attach the Floating IP to your test instance.
* [ ] Once the instance transitions to the ACTIVE state, SSH to it as the "cc" user via its Floating IP, using the private key associated with the Key Pair you set up.

### Edge-specific

* [ ] _If using reservations,_ navigate to the Lease menu and open the Device Calendar; ensure it shows each device you have enrolled and that they are not grayed out.
* [ ] Navigate to the Container view and launch a test container (i.e. `arm64v8/python`)
  * [ ] _If using reservations_, specify a "reservation" scheduler hint, with the value being the ID of the _reservation_ (not the lease) you made in the prior step.
  * [ ] Wait for the container to transition to Running state.
* [ ] Open the Console tab for the container and use the interactive shell to inspect the filesystem (or really any command.)
* [ ] Open the Logs tab and see if you get output (for some images this might be empty, but it should at least not throw an error.)
