#!/usr/bin/env python
import boto.ec2
import jinja2
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

    ec2_regions = {"us-east-1": "us-east",
                   "us-west-1": "us-west",
                   "us-west-2": "us-west-2",
                   "eu-west-1": "eu-ireland",
                   "ap-southeast-1": "apac-sin",
                   "ap-southeast-2": "apac-syd",
                   "ap-northeast-1": "apac-tokyo",
                   "sa-east-1": "sa-east-1"
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
    """
    Define instances weights
    """
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


def parse_instances(instances):
    """
    Wait for instance in running state
    """
    controller = None
    injectors = []
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

    return controller, injectors


def cloud_connect(region):
    """
    Connect on cloud
    """
    print "connect on {}...".format(region)

    conn = boto.ec2.connect_to_region(region)
    return conn


def write_ini(injectors, controller):
    """
    Write ansible .ini file
    """
    templateLoader = jinja2.FileSystemLoader(searchpath=".")
    templateEnv = jinja2.Environment(loader=templateLoader)

    templateVars = {"injectors": injectors,
                    "controller": controller}
    #
    # Configure the cluster
    #
    template = templateEnv.get_template("cluster.j2")
    clients = open("cluster.ini", 'w')
    clients.write(template.render(templateVars))
    clients.close()



if __name__ == "__main__":

    try:
        region = sys.argv[1]
    except:
        print "usage : ec2tool.py REGI0N"
        sys.exit(1)

    conn = cloud_connect(region)
    print "connected"

    instances = conn.get_all_instances()

    controller, injectors = parse_instances(instances)

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
        write_ini(injectors, controller)
        #
        print 'ansible-playbook -i cluster.ini -u ubuntu playbooks/tsung.yml'
