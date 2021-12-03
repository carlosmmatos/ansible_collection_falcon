#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ansible module to configure CrowdStrike Falcon Sensor on Linux systems.
# Copyright: (c) 2021, CrowdStrike Inc.

# Unlicense (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
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

import re

# import module snippets
from ansible.module_utils.basic import AnsibleModule

class FalconCtl(object):

    def __init__(self, module):
        self.module = module
        self.cs_path = "/opt/CrowdStrike"
        self.falconctl = self.module.get_bin_path('falconctl', required=True, opt_dirs=[self.cs_path])

        self.fargs = {
            "s": [
                "cid",
                "aid",
            ],
            "d": [
                "cid",
                "aid",
            ],

        }

        self.fstates = {"present": "s", "absent": "d"}
        self.has_changed = False

        self.state = module.params['state']
        self.force = module.params['force']
        self.params = module.params

        self.validate_params(self.params)
        if self.params['cid']:
            self.cid = self.validate_cid(self.params['cid'])

        args = self.add_args(self.state, self.params, self.force)
        self.falconctl_cmnd(args)

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

    def validate_cid(self, cid):
        """Verifies if a CID, as provided by the user, is valid"""
        valid_cid = re.match(
            '^[0-9a-fA-F]{32}-[0-9a-fA-F]{2}$', cid, flags=re.IGNORECASE)

        if not valid_cid:
            self.module.fail_json(
                msg="Invalid CrowdStrike CID: '%s'" % (cid))
        return valid_cid

    def cid_exists(self):
        """Returns boolean and value if CID has already been set"""
        cmd = [self.falconctl, "-g --cid"]
        rc, stdout, stderr = self.execute_command(cmd)
        if rc == 0:
            # CID has been set, extract value
            existing_cid = self.get_existing_cid(stdout)
            return True, existing_cid
        return False, stderr

    def compare_cids(self, cid1, cid2):
        """Checks to see if the existing CID matches the declared CID"""
        if cid1 in cid2.lower():
            return True
        return False

    def get_existing_cid(self, stdout):
        """Return existing str value of CID"""
        return re.search('cid="(.+?)".?', stdout).group(1)

    def handle_rc(self, rc):
        """Do something with the return code - basically error handling"""

        # Scenarios:
        # rc 0 is indicative of either a successful change w/o -f, or the use of -f.
        # For example, you can run falconctl -d -f --cid multiple times and it will
        # tell you it's fine.
        #
        # rc 255 is basically the error or something is already set code. It's a catchall.
        if rc == 0:
            if not self.force:
                self.has_changed = True

    def add_args(self, state, params, force):
        """Appends and adds all args to only run falconctl once"""
        args = [self.falconctl]
        fstates = self.fstates[state]

        args.append("-%s" % (fstates))
        if force:
            args.append("-f")

        for k in params:
            if k in self.fargs[fstates]:
                if state == "present":
                    args.append("--%s=%s" % (k, params[k]))
                else:
                    if not force:
                        # Deletion/absent tasks must use force
                        args.append("-f")
                    args.append("--%s" % (k))
        return args

    def execute_command(self, cmd):
        """Runs the falconctl command on the system"""
        rc, stdout, stderr = self.module.run_command(
            cmd, use_unsafe_shell=False)

        return rc, stdout, stderr

    def falconctl_cmnd(self, args):
        """If not in check mode, run the falconctl command"""
        if not self.module.check_mode:
            rc, stdout, stderr = self.execute_command(args)
            self.handle_rc(rc)
            self.module.exit_json(changed=self.has_changed)


def main():
    # Falconctl module supported parameters listed below
    fields = dict(
        state=dict(default="present", choices=['absent', 'present'], type="str"),
        cid=dict(required=False, no_log=False, type="str"),
        provisioning_token=dict(required=False, type="str"),
        force=dict(default=False, type="bool")
    )

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=True
    )

    FalconCtl(module)


if __name__ == '__main__':
    main()
