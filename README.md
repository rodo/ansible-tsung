ansible-tsung
=============

Ansible playbooks for Tsung deployment

Using
=====

1. launch your instances

2. tag one of them controller **tsung_role=controller**

3. build the list of instances

$ ec2tool.py playbooks/roles/tsung_scenario/templates


`$ cd `

Create a ssl key

`$ ssh-keygen -t dsa -f playbooks/roles/tsung/templates/id_dsa


AWS EC2
=======

Using this playbook on EC2

$ ansible-playbook -i "ec2-54-85-183-208.compute-1.amazonaws.com," -u ubuntu playbooks/tsung.yml
