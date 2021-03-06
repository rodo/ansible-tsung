ansible-tsung
=============

Ansible playbooks for Tsung deployment, install tsung from git
official repo, compile on each host. Configure a sample scenarion with
client cpu autoconfigure from instance type.  Works on EC2 with Ubuntu
image actually.

Create a user named **tsung** with a log directory ~/tsung/logs/
served on http by Yaws on port 8080 on controller.


Using
=====

1. launch your instances on EC2 or OpenStack

2. tag one of them as controller with **tsung_role=controller**

3. configure you cluster is as simple as run :

`$ python ec2tool.py REGION`

4. create the ssh key

`$ ssh-keygen -t dsa -f playbooks/roles/tsung/templates/id_dsa`

5. run ansible to set up the whole cluster

6. ssh to the **controller** and enjoy

Playbooks
=========

* munin.yml : deploy munin-node on all nodes, and munin on controller

* tsung.yml : deploy tsung on all nodes

Dependencies
============

Python libraries listed in `requirements.txt`

Datas
=====

* http://aws.amazon.com/ec2/pricing/json/linux-od.json
