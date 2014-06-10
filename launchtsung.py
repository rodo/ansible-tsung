#!/usr/bin/env python -u

import boto.ec2
import time
import threading
import sys
from uuid import uuid4

def launch_controller(region, ami, instance_type, tid):
    """
    Launch a Tsung controller
    """
    launch(region, ami, instance_type, tid, "controller", "controller")

def launch_injector(region, ami, instance_type, tid, nb):
    """
    Launch a Tsung injector
    """
    name = "injector {}".format(nb)
    launch(region, ami, instance_type, tid, "injector", name)


def launch(region, ami, instance_type, tid, role, name):
    """
    Launch an instance and Tag it

    - region (string)
    - ami (string)
    - instance_type (string)
    - tid (string)
    - role (string)
    - name (uuid)
    """
    print 'Launch {}'.format(name)
    conn = boto.ec2.connect_to_region(region)

    reservation = conn.run_instances(ami,
                                     key_name='rodo-virginia',
                                     instance_type=instance_type,
                                     security_groups=['tsung'])

    # NOTE: this isn't ideal, and assumes you're reserving one instance. Use a for loop, ideally.
    instance = reservation.instances[0]

    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        time.sleep(10)
        status = instance.update()

    sid = str(tid).split('-')[0]

    if status == 'running':
        instance.add_tag("tsung_role", role)
        instance.add_tag("tsung_cluster_id", tid)
        instance.add_tag("Name", "{} {}".format(sid, name))
        print('Instance {}, {} status: {}'.format(instance.id, role, status))
    else:
        print('Instance status: ' + status)


    # Now that the status is running, it's not yet launched. The only way to tell if it's fully up is to try to SSH in.
    if status == "running":
        retry = True
        while retry:
            try:
                # SSH into the box here. I personally use fabric
                retry = False
            except:
                time.sleep(10)

if __name__ == "__main__":

    region = "us-east-1"
    ami = 'ami-018c9568'
    instance_type = 't1.micro' #'c3.xlarge'
    tid = uuid4()    

    try:
        nb_injectors = int(sys.argv[1])
    except:
        nb_injectors = 2

    print "Cluster ID : {}".format(tid)

    cont = threading.Thread(None, launch_controller, None, (region, ami, instance_type, tid))
    cont.start()

    inst = 0
    while inst < nb_injectors:
        inst = inst + 1
        inj = threading.Thread(None, launch_injector, None, (region, ami, instance_type, tid, inst))
        inj.start()    

