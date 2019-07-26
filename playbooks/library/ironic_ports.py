#!/usr/bin/python

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=True),
        nics=dict(type='list',required=True),
        #state=dict(default='present', choices=['absent', 'present'])
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params['name']
    nics = module.params['nics']
    #state = module.params['state']

    sdk, cloud = openstack_cloud_from_module(module)

    # Find associated Ironic node
    try:
      node = cloud.get_machine(name)
      node_uuid = node['id']
    except:
      module.fail_json(msg="Cannot find Ironic node for %s." % name)

    try:
      ironic = cloud.baremetal
    except sdk.exceptions.OpenStackCloudException as e:
      module.fail_json(msg=e.message, extra_data=e.extra_data)

    messages = []
    nics_changed = False
    for nic in nics:
      # Find matching baremetal port by MAC
      # and verify that it is associated with this node
      # before attempting to update

      port_mac = nic['mac']
      this_nic = cloud.get_nic_by_mac(port_mac)
      if not this_nic:
        messages.append("Baremetal port with MAC %s not found." % port_mac)
      else:

        port_uuid = this_nic['id']

        if not this_nic['node_uuid'] == node_uuid:
          #TODO [codyhammock] Should we attempt to correct this condition?
          messages.append("Baremetal port with MAC %s is not associated with baremetal node %s! " % (port_mac,name) )
        else:

          nic_llc_data = this_nic['local_link_connection']

          nic_llc_config = {}
          for key in nic:
            if key != 'mac':
              nic_llc_config[key]= nic[key]

          # Add dummy value for 'switch_id', if not present
          # TODO [codyhammock] Ideally, this should be a real value, supplied by either configuration or discovery
          if not 'switch_id' in nic_llc_config:
            nic_llc_config['switch_id'] = '00:00:00:00:00:00'

          # Do we have all required parameters?
          if not all(key in nic_llc_config for key in ['switch_id', 'port_id', 'switch_info']):
            messages.append("Configuration for port with MAC %s is incomplete. %s" % ( port_mac, json.dumps(nic_llc_config) ) )
            continue

          # Determine configuration changes for output messaging
          patch_dict = dict( set( nic_llc_config.items() ) - set( nic_llc_data.items() ) )

          if patch_dict:
            try:
              cloud.set_machine_maintenance_state(node_uuid, state=True, reason="Node port udpate")
  
              update_nic = ironic.update_port(port=port_uuid, local_link_connection=nic_llc_config )
  
              messages.append("Port %s with MAC %s updated " % ( port_uuid, port_mac))
              messages.append(patch_dict)
              nics_changed = True
  
              cloud.set_machine_maintenance_state(node_uuid, state=False)
            except:
              module.fail_json(msg="Cannot update port")

    module.exit_json( changed=nics_changed, message=messages)

if __name__ == '__main__':
    main()
