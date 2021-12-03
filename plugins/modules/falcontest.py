#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
from hashlib import new
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
    # Class global variables
    module = None
    params = None
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

    def add_args(self, params, state):

        args = [self.falconctl, "-%s" % state]
        if



    ### STUBS ###
    def get_values(self):
        values = {}
        cmd = self.add_args(params, self.states["get"])
        for p in self.valid_params:
            if params[p]:
                # get current value
                cmd = ["/opt/CrowdStrike/falconctl", "-g"]
                cmd.append("--%s" % p)
                rc, stdout, stderr = self.module.run_command(
                    cmd, use_unsafe_shell=False)
                # append to before
                values.update({
                    p: {
                        "rc": rc,
                        "stdout": stdout
                    }
                })
        return values


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

    before = {}
    after = {}

    # BEFORE
    before = falcon.get_values()

    # Perform action set/delete
    falcon.execute()
    # for p in valid_params:
    #     cmd = ["/opt/CrowdStrike/falconctl"]
    #     if module.params[p]:
    #         # Set
    #         if module.params['state'] == 'present':
    #             # do something
    #             cmd.append("-s")
    #             cmd.append("-f")
    #             cmd.append("--%s=%s" % (p, module.params[p]))
    #         else:
    #             # delete
    #             cmd.append("-d")
    #             cmd.append("-f")
    #             cmd.append("--%s" % p)
    #         # Execute command
    #         rc, stdout, stderr = module.run_command(
    #             cmd, use_unsafe_shell=False)

    # After
    after = falcon.get_values()
    # Let's get the new values
    # for p in valid_params:
    #     if module.params[p]:
    #         # get current value
    #         cmd = ["/opt/CrowdStrike/falconctl", "-g"]
    #         # cmd.append("--%s" % p)
    #         rc, stdout, stderr = module.run_command(
    #             cmd, use_unsafe_shell=False)
    #         # append to before
    #         after.update({
    #             p: {
    #                 "rc": rc,
    #                 "stdout": stdout
    #             }
    #         })

    # module.fail_json(
    #   msg="before: %s POOP: %s" % (before, after)
    # )

    if before != after:
        result['changed'] = True
        result['diff'] = dict(
            before=before,
            after=after
        )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
