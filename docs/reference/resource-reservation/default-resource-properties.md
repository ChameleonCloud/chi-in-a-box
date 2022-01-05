# Default Resource Properties

### What are Default Resource Properties?

When a user creates a resource reservation, they include properties they want the reserved resource to match. For example, specifying the type of baremetal node to reserve, or a minimum amount of RAM. Default resource properties can be configured so that requests without resource properties, which would normally be unbounded, and will result in random resources being reserved, are given some set of constraints. This is may be desired when not all resources are equal. For example, when there is a mixture of x86 and ARM nodes, or when some nodes have GPUs.

### Configuration and Usage

The following configuration options can be set in `defaults.yml`

* `blazar_host_default_resource_properties` is the resource property array to use when none is given when creating a host reservation. Note that the `$` character must be escaped to `\$`. Setting this to  `'[]'` and changing `blazar_host_retry_without_default_resources` to false will use no default resource properties.&#x20;
* `blazar_host_retry_without_default_resources` is a boolean value, whether any defaults should be used if the allocation using default resource properties fails.&#x20;
* `blazar_network_default_resource_properties` is the resource property array to use when none is given when creating a network reservation. Note that the `$` character must be escaped to `\$`. Setting this to  `'[]'` and changing `blazar_network_retry_without_default_resources` to false will use no default resource properties.&#x20;
* `blazar_network_retry_without_default_resources` is a boolean value, whether any defaults should be used if the allocation using default resource properties fails.&#x20;
