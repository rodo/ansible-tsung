ansible-tsung
=============

Ansible playbooks for Tsung deployment

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

Dependencies
============

Python libraries listed in `requirements.txt`
