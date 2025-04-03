**Summary**: One of the OpenStack APIs is returning a different HTTP code than expected, OR we are failing to get any response from it.

**Consequences**: If one of the OpenStack APIs is indeed down, or returning error codes, it will affect the reliability of the cluster as a whole, and large portions of the testbed may not be working.

### Possible causes

**Failure of monitoring to contact cluster**: this alert depends on metrics that are gathered by an external source (a Prometheus OpenStack metric exporter), and if the exporter fails to authenticate or otherwise cannot reach the cluster, this alert can fire, though nothing is really on 🔥.

**Recent upgrade changed default HTTP codes**: If an OpenStack API is returning a weird code, it could be an unexpected side effect of a deploy, where a service used to return a code 200 on the root (`/`) endpoint, and now it's returning 204 (for example.)

1. What happens when you `curl -i $endpoint/` for the service? See what code is returned, and if it makes sense to return that code.
2. If this is indeed an instance of bad alerting, make an update to the [monitoring code](https://github.com/ChameleonCloud/prometheus-openstack-exporter/blob/master/exporter/check_os_api.py#L28-L56) to look for the updated return code.

**Service failure**: It could be that the OpenStack service is actually not healthy. Try the following if this is the case:

1. Verify that the service appears healthy; usually a smoke test through the system is enough.
2. If not, is the service running? Check the running Docker containers for any containers in a restart loop.
3. Examine the logs for the service for errors: `docker run --rm -v kolla_logs:/logs centos:7 grep -i ERROR /logs/$service/$component`. This can usually tell you what's wrong.


