#!/usr/bin/env python

# Copyright 2020 Jason Anderson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import os

from ansible import constants
from ansible.errors import AnsibleError, AnsibleAction, AnsibleActionFail
from ansible.module_utils._text import to_text
from ansible.playbook.play_context import PlayContext
from ansible.plugins import action

DEFAULT_STOP_TIMEOUT = 2 # seconds
SYSTEMD_SERVICE_NAME_PATTERN = r"[a-zA-Z0-9\.\-_]+"

DOCUMENTATION = '''
---
module: chi_docker_service
short_description: Deploy a secondary CHI-in-a-Box Docker service
description:
     - Some services for CHI-in-a-Box are not provided by Kolla-Ansible, such
       as JupyterHub and Redfish SEL monitoring. This module provides support
       for provisioning those services via systemd and Docker.
options:
  name:
    description:
      -
    required: True
    type: str
  image:
    description:
      -
    required: True
    type: str
  command:
    description:
      -
    required: False
    type: str
  network:
    description:
      -
    required: False
    type: str
  mounts:
    description:
      -
    required: False
    type: list
  environment:
    description:
      -
    required: False
    type: dict
  ports:
    description:
      -
    required: False
    type: list
author: Jason Anderson
'''

EXAMPLES = '''
Deploy a simple Docker service:

- hosts: control
  tasks:
    - name: Configure a simple service or cluster of services.
      chi_docker_service:
        name: my_service
        image: docker.chameleoncloud.org/my_service:latest
        volumes:
          - type: bind

'''

class ActionModule(action.ActionBase):

    TRANSFERS_FILES = True

    def _get_template_action_plugin(self):
        return (self._shared_loader_obj.action_loader.get(
            'template',
            task=self._task.copy(),
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj))

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp # No longer used

        module_args = self._task.args.copy()

        name = module_args.get("name", None)
        image = module_args.get("image", None)
        command = module_args.get("command", None)
        network = module_args.get("network", None)
        mounts = module_args.get("mounts", [])
        ports = module_args.get("ports", [])
        environment = module_args.get("environment", {})
        bind_address = module_args.get("bind_address", task_vars.get("api_interface_address"))
        stop_timeout = module_args.get("stop_timeout", DEFAULT_STOP_TIMEOUT)

        try:
            if not (name and image):
                raise AnsibleActionFail("name and image are required")
            if re.match(SYSTEMD_SERVICE_NAME_PATTERN, name) is None:
                raise AnsibleActionFail((
                    "name must be a valid systemd service name"))
            if not isinstance(mounts, list):
                raise AnsibleActionFail("mounts must be a list")
            if not all(self._is_valid_mount(m) for m in mounts):
                raise AnsibleActionFail((
                    "mounts must be valid Docker mount declarations"))
            if not isinstance(ports, list):
                raise AnsibleActionFail("ports must be a list")
            if not all(self._is_valid_port(p) for p in ports):
                raise AnsibleActionFail((
                    "ports must be valid Docker port declarations"))
            if not isinstance(environment, dict):
                raise AnsibleActionFail("environment must be a dict")

            formatted_mounts = [self._format_run_mount(m) for m in mounts]

        except AnsibleAction:
            raise
        except Exception as e:
            raise AnsibleActionFail("%s: %s" % (type(e).__name__, to_text(e)))

        task_vars.update(
          service=dict(
            name=name,
            image=image,
            command=command,
            network=network,
            mounts=formatted_mounts,
            ports=ports,
            environment=environment,
            bind_address=bind_address,
            stop_timeout=stop_timeout
          )
        )

        source = os.path.join(
          os.getenv("ANSIBLE_TEMPLATES"),
          "chi_docker_service_systemd.service.j2"
        )

        template_module_args = dict(
            src=source,
            dest="/usr/lib/systemd/system/{}.service".format(name)
        )
        template_action = self._get_template_action_plugin()
        template_action._task.args = template_module_args
        result.update(template_action.run(task_vars=task_vars))

        if result.get("failed"):
            return result

        service_module_args = dict(
            name=name,
            state="started",
            enabled=True
        )
        result.update(self._execute_module(module_name="systemd",
                                           module_args=service_module_args,
                                           task_vars=task_vars))

        return result

    def _is_valid_mount(self, mount):
        return all(k in mount for k in ["type", "src", "dst"])

    def _is_valid_port(self, port):
        parts = port.split(":")
        return len(parts) == 2 and all(p.isdigit() for p in parts)

    def _format_run_mount(self, mount):
        mount_str = "type={},src={},dst={}".format(mount.get("type"),
                                                   mount.get("src"),
                                                   mount.get("dst"))
        if mount.get("readonly"):
            mount_str += ",readonly"
        return mount_str
