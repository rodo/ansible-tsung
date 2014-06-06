#!/usr/bin/env python
import boto.ec2
import os
import jinja2
import copy
import sys

class Tsing(boto.ec2.instance.Instance):
    
    def shortname(self):
        return self.private_dns_name.split('.')[0]

    @property
    def private_short_name(self):
        return self.private_dns_name.split('.')[0]

if __name__ == "__main__":

    try:
        region = sys.argv[1]
    except:
        region = "us-east-1"


    print "connect on {}...".format(region)

    conn = boto.ec2.connect_to_region(region)

    print "connected"

    instances = conn.get_all_instances()

    privattr =  ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', 
             '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', 
             '__subclasshook__', '__weakref__', 
             '_in_monitoring_element', '_placement', '_previous_state', '_state', '_update']

    pubattr = ['ami_launch_index', 'architecture', 'block_device_mapping', 
               'client_token', 'connection', 
               'dns_name', 'ebs_optimized',  'eventsSet', 
               'group_name', 'groups', 
               'hypervisor', 
               'instance_profile', 'instance_type', 'interfaces', 'ip_address', 'item', 'kernel', 
               'key_name', 'launch_time', 
               'monitored', 'monitoring', 'monitoring_state', 
               'persistent', 'placement', 'placement_group', 
               'placement_tenancy', 'platform', 'previous_state', 
               'previous_state_code', 'private_dns_name', 'private_ip_address', 'product_codes', 'public_dns_name', 
               'ramdisk', 'reason', 
               'region', 
               'requester_id',
               'root_device_name', 'root_device_type', 'spot_instance_request_id', 
               'state', 'state_code', 'state_reason', 
               'subnet_id', 'tags',  'virtualization_type', 
               'vpc_id']
    
    meth = ['start', 'startElement','remove_tag','reboot', 'terminate', 'unmonitor', 'update', 'use_ip',
            'stop', 'reset_attribute', 'get_attribute', 'modify_attribute', 
            'monitor','confirm_product', 'create_image', 'add_tag', 'get_console_output',
            'endElement',
            ]

    nodes = []
    injectors = []
    controller = None

    for instance in instances:
        inst = instance.instances[0]
        
        print "{} {} {}".format(inst.id, inst.image_id, inst.state)
        for attr in pubattr:
            print " - {} : {}".format(attr, inst.__getattribute__(attr))

