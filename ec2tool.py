#!/usr/bin/env python
import boto.ec2
import os
import jinja2
import copy

conn = boto.ec2.connect_to_region("us-east-1")

instances = conn.get_all_instances()

class Tsing(boto.ec2.instance.Instance):
    
    def shortname(self):
        return self.private_dns_name.split('.')[0]

    @property
    def private_short_name(self):
        return self.private_dns_name.split('.')[0]


"""
['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_in_monitoring_element', '_placement', '_previous_state', '_state', '_update', 'add_tag', 'ami_launch_index', 'architecture', 'block_device_mapping', 'client_token', 'confirm_product', 'connection', 'create_image', 'dns_name', 'ebs_optimized', 'endElement', 'eventsSet', 'get_attribute', 'get_console_output', 'group_name', 'groups', 'hypervisor', 'id', 'image_id', 'instance_profile', 'instance_type', 'interfaces', 'ip_address', 'item', 'kernel', 'key_name', 'launch_time', 'modify_attribute', 'monitor', 'monitored', 'monitoring', 'monitoring_state', 'persistent', 'placement', 'placement_group', 'placement_tenancy', 'platform', 'previous_state', 'previous_state_code', 'private_dns_name', 'private_ip_address', 'product_codes', 'public_dns_name', 'ramdisk', 'reason', 'reboot', 'region', 'remove_tag', 'requester_id', 'reset_attribute', 'root_device_name', 'root_device_type', 'spot_instance_request_id', 'start', 'startElement', 'state', 'state_code', 'state_reason', 'stop', 'subnet_id', 'tags', 'terminate', 'unmonitor', 'update', 'use_ip', 'virtualization_type', 'vpc_id']
"""
nodes = []
injectors = []
controller = None

for instance in instances:
    inst = instance.instances[0]
    inst.__class__ = Tsing
    if inst.state == 'running':
        tags = inst.tags
        
        if 'tsung_role' in tags:
            if tags['tsung_role'] == 'controller':
                controller = inst
            else:
                injectors.append(inst)
        else:
            injectors.append(inst)
#
#
#
print "found {} injectors".format(len(injectors))
print "controller tsung@{} ".format(controller.ip_address)
#
#
#
hosts = open("playbooks/roles/tsung/vars/nodes.yml", 'w')
hosts.write("---\n")
hosts.write("controller: { private_dns_name: '%s', private_ip_address: '%s', private_short_name: '%s' }\n\n" % (controller.private_dns_name,
                                                                                                                controller.private_ip_address,
                                                                                                                controller.private_short_name))
hosts.write("injectors:\n")
for injec in injectors:
    hosts.write("  - { private_dns_name: '%s', private_ip_address: '%s', private_short_name: '%s' }\n" % (injec.private_dns_name, 
                                                                                                          injec.private_ip_address,
                                                                                                          injec.private_short_name))
hosts.close()
#
#
#
templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader )

templateVars = {"injectors": injectors,
                "controller": controller}

#
# Configure the cluster
#
template = templateEnv.get_template( "cluster.j2" )

clients = open("cluster.ini", 'w')
clients.write(template.render(templateVars))
clients.close()

#
#
print 'ansible-playbook -i cluster.ini -u ubuntu playbooks/tsung.yml'
