#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: sensor_update_policy

short_description: Manage sensor update policies

version_added: "4.0.0"

description:
  - Manage sensor update policies with CrowdStrike Falcon API.
  - See the L(Falcon documentation,https://falcon.crowdstrike.com/documentation/page/d2d629cf/sensor-update-policies)
    for more information about sensor update policies.

options:
  build:
    description:
      - The build version this sensor update policy applies to.
    type: str
  description:
    description:
      - The description of the sensor update policy.
    type: str
  name:
    description:
      - The name of the sensor update policy.
    type: str
  platform_name:
    description:
      - The name of the OS platform this sensor update policy applies to.
    type: str
    choices:
      - Windows
      - Linux
      - Mac
  scheduler:
    description:
      - Dictionary containing the scheduler settings for this sensor update policy.
    type: dict
  show_early_adopter_builds:
    description:
      - Whether or not to show early adopter builds for this sensor update policy.
    type: bool
  uninstall_protection:
    description:
      - Whether or not to enable uninstall protection for this sensor update policy.
    type: str
    choices: ['ENABLED', 'DISABLED']
  variants:
    description:
      - List of dictionaries containing the sensor update policy variants.
      - If the parameters in the variant are true when hosts are evaluated, the
        build in the variant array is used instead of the build specified by the
        sensor policy I(build) option.
    type: list
    elements: dict

extends_documentation_fragment:
    - crowdstrike.falcon.credentials
    - crowdstrike.falcon.credentials.auth

author:
  - Carlos Matos (@carlosmmatos)
"""

EXAMPLES = r"""
- name: Create a Sensor Update Policy
  crowdstrike.falcon.sensor_update_policy:
    name: "Windows 10 Sensor Policy"
    description: "Windows 10 Sensor Policy"
    platform_name: "Windows"
    build: "
"""
