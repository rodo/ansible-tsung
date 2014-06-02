ansible-tsung
=============

Ansible playbooks for Tsung deployment

Using
=====

`$ cd playbooks/`

Create a ssl key

`$ ssh-keygen -t dsa -f roles/tsung/templates/id_dsa


AWS EC2
=======

Using this playbook on EC2

$ ansible-playbook -i "ec2-54-85-183-208.compute-1.amazonaws.com," -u ubuntu playbooks/tsung.yml
