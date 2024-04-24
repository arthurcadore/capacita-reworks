#!/usr/bin/python


DOCUMENTATION = '''
---

module: comware_intfState
short_description: Check the port status. If there are undo shutdown ports but the field ports are down, 
                   list these inconsistent ports. If not, return OK.
description:
    - .
version_added: 1.0
category: System (RW)
author: gongqianyu
options:
    hostname:
        description:
            - IP Address or hostname of the Comware 7 device that has
              NETCONF enabled
        required: true
        default: null
        choices: []
        aliases: []
    username:
        description:
            - Username used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    password:
        description:
            - Password used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    port:
        description:
            - NETCONF port number
        required: false
        default: 830
        choices: []
        aliases: []
    look_for_keys:
        description:
            - Whether searching for discoverable private key files in ~/.ssh/
        required: false
        default: False
        choices: []
        aliases: []

'''
EXAMPLES = '''

# - name: Check the port status
#   comware_intfState: username={{ username }} password={{ password }} hostname={{ inventory_hostname }}
'''

import socket
import os
import time


try:
    HAS_PYCW7 = True
    from pycw7.comware import COM7
    from pycw7.features.errors import *
    from pycw7.features.intfState import IntfState
except ImportError as ie:
    HAS_PYCW7 = False


def safe_fail(module, device=None, **kwargs):
    if device:
        device.close()
    module.fail_json(**kwargs)


def safe_exit(module, device=None, **kwargs):
    if device:
        device.close()
    module.exit_json(**kwargs)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            port=dict(default=830, type='int'),
            hostname=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            look_for_keys=dict(default=False, type='bool'),
        ),
        supports_check_mode=True
    )
    if not HAS_PYCW7:
        module.fail_json(msg='There was a problem loading from the pycw7 '
                             + 'module.', error=str(ie))

    username = module.params['username']
    password = module.params['password']
    port = module.params['port']
    hostname = socket.gethostbyname(module.params['hostname'])
    device_args = dict(host=hostname, username=username,
                       password=password, port=port)
    device = COM7(**device_args)
    # proposed = dict((k, v) for k, v in args.items() if v is not None)

    changed = False
    commands = []
    try:
        look_for_keys = module.params['look_for_keys']
        device.open(look_for_keys=look_for_keys)
    except ConnectionError as e:
        safe_fail(module, device, msg=str(e),
                  descr='error opening connection to device')

    COMPARE = IntfState(device)

    check = COMPARE.get_result()

    if check == False:
        print ('ok')

    else:

        module.fail_json(msg=check)

    if device.staged:

        commands = device.staged_to_string()
        if module.check_mode:
            safe_exit(module, device, changed=True,
                      commands=commands)
        else:
            try:
                device.execute_staged()
            except PYCW7Error as e:
                safe_fail(module, device, msg=str(e),
                          descr='error during execution')
            changed = True

    results = {}
    results['commands'] = commands
    results['changed'] = changed
    # results['proposed'] = proposed

    safe_exit(module, device, **results)

from ansible.module_utils.basic import *

main()
