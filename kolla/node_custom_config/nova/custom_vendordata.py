# Copyright 2017 University of Chicago
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Populate Vendordata with information required by Chameleon."""

from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client
from nova.api.metadata import base
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class CustomVendorData(base.VendorDataDriver):
    def __init__(self, *args, **kwargs):
        super(CustomVendorData, self).__init__(*args, **kwargs)
        data = {
          "auth_url": "{{ keystone_public_url }}",
          "auth_url_v2": "{{ keystone_public_url }}/v2.0",
          "auth_url_v3": "{{ keystone_public_url }}/v3",
          "cluster": "chameleon",
          "grid": "chameleoncloud",
          "node": kwargs["instance"]["node"],
          "site": "{{ chameleon_site_name }}",
          "region": "{{ openstack_region_name }}",
          "user_id": kwargs["instance"]["user_id"],
          "project_id": kwargs["instance"]["project_id"],
        }
        try:
            auth = v3.Password(auth_url='{{ keystone_public_url }}/v3',
                               username='{{ instance_metrics_writer_username }}',
                               password='{{ instance_metrics_writer_password }}',
                               project_id=kwargs['instance']['project_id'],
                               user_domain_id='default',
                               project_domain_id='default')
            sess = session.Session(auth=auth)
            token = auth.get_token(sess)
            data['instance_metrics_writer_token'] = token
        except Exception as e:
            LOG.exception("Exception %s while creating instance_metrics_writer token for ChameleonCloudVendorData" % str(e))

        self._data = data

    def get(self):
        return self._data
