# User support guide

To assist you in handling user questions or requests, here are a few common problems that have been encountered over the years, and how to solve them (please add if any new ones come up!)

## Networking

### User cannot delete Neutron network

Usually this is because the user does not understand the dependency-order of all the Neutron abstractions. In order to delete a network, one first must remove its subnets from any routers, then delete the subnets, and finally delete the network. It is such a common operation that python-chi maintains the [`nuke_network`](https://python-chi.readthedocs.io/en/latest/modules/network.html#chi.network.nuke\_network) helper.
