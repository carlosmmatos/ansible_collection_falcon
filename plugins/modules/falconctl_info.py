#!/usr/bin/python

# Copyright: (c) 2020, Your Name <YourName@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: falconctl_info

short_description: Get values associated with Falcon sensor.

version_added: "1.0.0"

description:
  - Return value associated with the Falcon sensor options.
  - This module is similar to the GET option in falconctl cli.

options:
  name:
    description:
      - A list of falconctl GET options to query.
    choices: [
        'cid',
        'aid',
        'apd',
        'aph',
        'app',
        'trace',
        'feature',
        'metadata_query',
        'message_log',
        'billing',
        'tags',
        'provisioning_token'
        ]
    type: list
    elements: str

author:
  - Carlos Matos <matosc15@gmail.com>
  - Gabriel Alford <redhatrises@gmail.com>
'''

EXAMPLES = r'''
- name: Get all Falcon sensor options
  crowdstrike.falcon.falconctl_info:

- name: Get a subset of Falcon sensor options
  crowdstike.falcon.falconctl_info:
    name:
      - 'cid'
      - 'aid'
      - 'tags'
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
my_useful_info:
    description: The dictionary containing information about your system.
    type: dict
    returned: always
    sample: {
        'foo': 'bar',
        'answer': 42,
    }
'''

import re
from ansible.module_utils.basic import AnsibleModule

class FalconCtlInfo(object):

    def __init__(self, module, choices):
        self.module = module
        self.choices = choices
        self.name = module.params['name']
        self.cs_path = "/opt/CrowdStrike"
        self.falconctl = self.module.get_bin_path(
            'falconctl', required=True, opt_dirs=[self.cs_path])


    def get_options(self):
        self.values = {}
        # Collect only options passed in via 'name'
        if self.name:
            for p in self.name:
                # Add value to dict
                key = p.replace("_", "-")
                rc, stdout = self.__execute_command(key)
                stdout_new = self.__format_stdout(stdout)
                self.values.update({
                    p: stdout_new
                })
        else:
            for p in self.choices:
                # Add value to dict
                key = p.replace("_", "-")
                rc, stdout = self.__execute_command(key)
                stdout_new = self.__format_stdout(stdout)
                self.values.update({
                    p: stdout_new
                })
                # self.module.fail_json(
                #     msg = "%s" % self.values
                # )

        return self.values

    def __format_stdout(self, stdout):
        if stdout == "" or "not set" in stdout:
            return "null"
        else:
            # Expect stdout in <option>=<value>
            return re.sub("[\"\s\\n\.]", "", stdout).split("=")[1]


    def __execute_command(self, option):
        cmd = [self.falconctl, "-g"]
        cmd.append("--%s" % option)
        rc, stdout, stderr = self.module.run_command(
            cmd, use_unsafe_shell=False)
        return rc, stdout



def main():
    # define available arguments/parameters a user can pass to the module
    _choices = [
        'cid',
        'aid',
        'apd',
        'aph',
        'app',
        'trace',
        'feature',
        'metadata_query',
        'message_log',
        'billing',
        'tags',
        'provisioning_token'
        ]
    module_args = dict(
        name=dict(type='str', required=False, choices=_choices),
    )

    result = dict(
        changed=False,
        falconctl_info={}
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    falconctl_info = FalconCtlInfo(module, _choices)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['falconctl_info'] = falconctl_info.get_options()

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

if __name__ == '__main__':
    main()
