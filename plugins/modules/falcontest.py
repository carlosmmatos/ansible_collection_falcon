#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ansible module to configure CrowdStrike Falcon Sensor on Linux systems.
# Copyright: (c) 2021, CrowdStrike Inc.

# Unlicense (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
import re
__metaclass__ = type


DOCUMENTATION = """
---
module: falconctl
author:
  - Gabriel Alford <redhatrises@gmail.com>
  - Carlos Matos <matosc15@gmail.com>
short_description: Configure CrowdStrike Falcon Sensor
description:
  - Configures CrowdStrike Falcon Sensor on Linux systems
options:
    cid:
      description:
        - CrowdStrike Falcon Customer ID (CID).
      type: str
    state:
      description:
        - If falconctl will set, delete, or only return configuration settings.
      type: str
      default: present
      choices: [ absent, present ]
    force:
      description:
        - Force falconctl to configure settings.
      type: bool
      default: 'no'
    provisioning_token:
      description:
        - Installation tokens prevent unauthorized hosts from being accidentally or maliciously added to your customer ID (CID).
        - Optional security measure for your CID.
      type: str
extends_documentation_fragment:
    - action_common_attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
    platform:
        support: full
        platforms: posix
"""

EXAMPLES = """
- name: Set CrowdStrike Falcon CID
  crowdstrike.falcon.falconctl:
    state: present
    cid: 1234567890ABCDEF1234567890ABCDEF-12

- name: Delete CrowdStrike Falcon CID
  crowdstrike.falcon.falconctl:
    state: absent
    cid: 1234567890ABCDEF1234567890ABCDEF-12
"""


class FalconCtl(object):
    valid_params = [
        "cid",
        "provisioning_token"
    ]

    def __init__(self, module):
        self.module = module
        self.params = self.module.params

        self.cs_path = "/opt/CrowdStrike"
        self.falconctl = self.module.get_bin_path(
            'falconctl', required=True, opt_dirs=[self.cs_path])
        self.states = {"present": "s", "absent": "d", "get": "g"}
        self.state = self.params['state']

    def validate_params(self, params):
        """Check parameters that are conditionally required"""
        # Currently we have a condition for provisioning_token and cid. However,
        # the default ansible required_if module is very limiting in terms of dealing
        # with strings so we handle it here.
        if params['provisioning_token']:
            # Ensure cid is also passed
            if not params['cid']:
                self.module.fail_json(
                    msg="provisioning_token requires cid!"
                )

    def validate_regex(self, cid):
        """Verifies if a CID, as provided by the user, is valid"""
        valid_cid = re.match(
            '^[0-9a-fA-F]{32}-[0-9a-fA-F]{2}$', cid, flags=re.IGNORECASE)

        if not valid_cid:
            self.module.fail_json(
                msg="Invalid CrowdStrike CID: '%s'" % (cid))
        return valid_cid

    def add_args(self, state):
        fstate = self.states[state]
        args = [self.falconctl, "-%s" % fstate]

        if state != "get":
            args.append("-f")

        for k in self.params:
            if k in self.valid_params:
                if state == "present":
                    args.append("--%s=%s" %
                                (k.replace("_", "-"), self.params[k]))
                else:
                    args.append("--%s" % (k.replace("_", "-")))
        return args

    def get_values(self):
        values = {}
        # Since there is no "get" state, we will pass it in here
        cmd = self.add_args("get")
        # get current values
        rc, stdout = self.__run_command(cmd)
        # append to dict
        values.update({
            "rc": rc,
            "stdout": stdout
        })
        return values

    def __run_command(self, cmd):
        rc, stdout, stderr = self.module.run_command(
            cmd, use_unsafe_shell=False)
        # Only return what we really want
        return rc, stdout

    def execute(self):
        cmd = self.add_args(self.params['state'])
        self.__run_command(cmd)


def main():
    module_args = dict(
        state=dict(default="present", choices=[
                   'absent', 'present'], type="str"),
        cid=dict(required=False, no_log=False, type="str"),
        provisioning_token=dict(required=False, type="str")
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # Instantiate class
    falcon = FalconCtl(module)

    result = dict(
        changed=False
    )

    # BEFORE
    before = falcon.get_values()

    # Perform action set/delete
    falcon.execute()

    # After
    after = falcon.get_values()

    if before != after:
        result['changed'] = True
        result['diff'] = dict(
            before=before,
            after=after
        )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
