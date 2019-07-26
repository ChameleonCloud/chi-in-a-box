#!/usr/bin/python

#import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

def _get_blazar_hosts(reservation):
  req_url = reservation.get_endpoint() + "/os-hosts"
  return reservation.get(url=req_url).json()

def _get_host_by_hostname(reservation, hostname):
  hosts = _get_blazar_hosts(reservation)
  for host in hosts['hosts']:
    if host['hypervisor_hostname'] == hostname:
      return host
  return None

def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=False),
        node_type=dict(required=False),
        state=dict(default='present', choices=['absent', 'present'])
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params['name']
    node_type = module.params['node_type']
    state = module.params['state']

    sdk, cloud = openstack_cloud_from_module(module)

    # Find associated Ironic node
    try:
      node = cloud.get_machine(name)
      node_uuid = node['id']
    except:
      module.fail_json(msg="Cannot find Ironic node for %s." % name)
  
    try:
      blazar = cloud.reservation

      if module.params['state'] == 'present':

        host_data = dict(
          name=node_uuid,
          node_type=node_type
        )
            
        # Does a host already exist for this hypervisor_hostname?
        host = _get_host_by_hostname(blazar, node_uuid)
        if not host:
          # No host, so add one

          req_url = "%s/os-hosts" % (blazar.get_endpoint())
          new_host = blazar.post(url=req_url, json=host_data).json()
          if 'error_code' in new_host:
            module.fail_json(msg=new_host['error_message'])

          module.exit_json( changed=True, result="Node added.", changes=new_host)

        else: # Host exists

          # Does it need to be updated?
          try:
            host_config = dict(
              name=host['hypervisor_hostname'],
              node_type=host['node_type']
            )
          except:
            host_config = dict(
              name=host['hypervisor_hostname'],
            )
         
          # Determine configuration change(s)   
          patch_dict = dict( set(host_data.items()) - set(host_config.items()))

          if patch_dict:
            req_url = "%s/os-hosts/%s" % (blazar.get_endpoint(), host['id'])

            update_host = blazar.put(url=req_url, json=patch_dict).json()
            if 'error_code' in update_host:
              module.fail_json(msg=update_host['error_message'])

            module.exit_json(changed=True, result="Node updated", changes=patch_dict)
          else:
            module.exit_json(changed=False, result="Node not updated")

      else:
        module.exit_json(changed=False, msg="Removing hosts is not currently supported.")


    except sdk.exceptions.OpenStackCloudException as e:
            module.fail_json(msg=e.message, extra_data=e.extra_data)



if __name__ == '__main__':
    main()
