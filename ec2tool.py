#!/usr/bin/env python
import boto.ec2
import os
import jinja2
import copy
import sys
import json
import yaml

class Tsing(boto.ec2.instance.Instance):

    def shortname(self):
        return self.private_dns_name.split('.')[0]

    @property
    def private_short_name(self):
        return self.private_dns_name.split('.')[0]


def get_specs(instance, region, data):
    """

    region (string) : the region name
    data (dict)
    """
    datas = get_data_region(region, data)
    instance_spec = get_instance(instance, datas)

    return instance_spec

def get_instance(instance, data):
    """
    instance (string)
    data (dict)
    """
    result = None
    for inst in data['instanceTypes']:
        for size in inst['sizes']:
            if instance == size['size']:
                result = size
                break

    return result


def get_data_region(region, data):
    """

    region (string) : the region name
    data (dict)
    """
    config = data['config']

    ec2_regions = {"us-east-1" : "us-east",
                   "us-west-1" : "us-west",
                   "us-west-2" : "us-west-2",
                   "eu-west-1" : "eu-ireland",
                   "ap-southeast-1" : "apac-sin",
                   "ap-southeast-2" : "apac-syd",
                   "ap-northeast-1" : "apac-tokyo",
                   "sa-east-1" : "sa-east-1"
                   }

    for reg in config['regions']:
        if reg['region'] == ec2_regions[region]:
            return reg


def write_nodes(controller, injectors, data):
    """

    controller (dict)
    injectors (dict)
    """
    hosts = open("playbooks/roles/tsung/vars/nodes.yml", 'w')
    hosts.write("---\n")
    contr_str = "controller: { private_dns_name: '%s', private_ip_address: '%s', private_short_name: '%s' }\n\n"
    hosts.write(contr_str % (controller.private_dns_name,
                             controller.private_ip_address,
                             controller.private_short_name))
    hosts.write("injectors:\n")
    for injec in injectors:
        print injec.__dict__
        specs = get_specs(injec.instance_type, region, data)
        injector = {"private_dns_name": str(injec.private_dns_name),
                    "private_ip_address": str(injec.private_ip_address),
                    "private_short_name": str(injec.private_short_name),
                    "instance_type": str(injec.instance_type),
                    "cpu": int(specs['vCPU'])}

        hosts.write(" - {}".format(yaml.dump(injector, encoding='utf-8')))
    hosts.close()


def instance_weights(injectors, region, data):

    assw = {}
    weights = []

    for injec in injectors:
        specs = get_specs(injec['instance_type'], region, data)
        weights.append(float(specs['memoryGiB']))

    minweight = min(weights)

    for injec in injectors:
        specs = get_specs(injec['instance_type'], region, data)
        iid = injec['id']
        assw[iid] = int(round(float(specs['memoryGiB']) / minweight))

    return assw


if __name__ == "__main__":

    try:
        region = sys.argv[1]
    except:
        print "usage : ec2tool.py REGI0N"
        sys.exit(1)

    print "connect on {}...".format(region)

    conn = boto.ec2.connect_to_region(region)

    print "connected"

    instances = conn.get_all_instances()

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
    print "found\n {} injectors".format(len(injectors))

    if controller is None:
        print "ERROR didn't found any controller"
        sys.exit(1)
    else:
        print " controller : tsung@{} ".format(controller.ip_address)
        #
        #
        with open("linux-od.json") as data_file:
            data = json.load(data_file)

        #
        #
        write_nodes(controller, injectors, data)
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
