#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest
import urllib2
sys.path.append('./')

from ec2tool import *
from test_datas import datas

class Tests(unittest.TestCase):
    """Main parts"""
    def setUp(self):

        self.injectors = [{'kernel': u'aki-919dcaf8', 'instance_profile': None,
                           'root_device_type': u'ebs', 'private_dns_name': u'ip-172-31-47-212.ec2.internal',
                           '_state': 'running(16)',
                           'group_name': None,
                           'public_dns_name': u'ec2-54-209-225-143.compute-1.amazonaws.com', 'id': u'i-7277bf20',
                           'state_reason': None,
                           'monitored': False,
                           'item': u'\n                ',
                           'subnet_id': u'subnet-05ddff2d',
                           'platform': None,
                           'eventsSet': None,
                           'ebs_optimized': False,
                           'client_token': '',
                           '_in_monitoring_element': False,
                           'virtualization_type': u'paravirtual', 'architecture': u'x86_64', 'ramdisk': None, '_previous_state': None,
                           'tags': {u'tsung_role': u'injector', u'Name': u'injector 1'},
                           'key_name': u'barack-angela',
                           'image_id': u'ami-018c9568', 'reason': '',
                           'spot_instance_request_id': None,
                           'monitoring': u'\n                    ',
                           'requester_id': None,
                           'ip_address': u'54.209.225.143', 'monitoring_state': u'disabled',
                           '_placement': 'us-east-1d',
                           'ami_launch_index': u'0',
                           'dns_name': u'ec2-54-209-225-143.compute-1.amazonaws.com',
                           'launch_time': u'2014-06-06T11:01:52.000Z',
                           'persistent': False,
                           'instance_type': u't1.micro',
                           'root_device_name': u'/dev/sda1',
                           'hypervisor': u'xen',
                           'private_ip_address': u'172.31.47.212', 'vpc_id': u'vpc-080bc76d', 'product_codes': []},
                          {'kernel': u'aki-919dcaf8', 'instance_profile': None,
                           'root_device_type': u'ebs', 'private_dns_name': u'ip-172-31-45-53.ec2.internal',
                           '_state': 'running(16)',
                           'group_name': None,
                           'public_dns_name': u'ec2-107-23-73-18.compute-1.amazonaws.com',
                           'id': u'i-e78942b5', 'state_reason': None,
                           'monitored': False, 'item': u'\n                ',
                           'subnet_id': u'subnet-05ddff2d',
                           'platform': None,
                           'eventsSet': None, 'ebs_optimized': False,
                           'client_token': '', '_in_monitoring_element': False, 'virtualization_type': u'paravirtual',
                           'architecture': u'x86_64', 'ramdisk': None,
                           '_previous_state': None, 'tags': {},
                           'key_name': u'barack-angela',
                           'image_id': u'ami-018c9568',
                           'reason': '',
                           'spot_instance_request_id': None, 'monitoring': u'\n                    ',
                           'requester_id': None,
                           'ip_address': u'107.23.73.18',
                           'monitoring_state': u'disabled', '_placement': 'us-east-1d',
                           'ami_launch_index': u'0',
                           'dns_name': u'ec2-107-23-73-18.compute-1.amazonaws.com',
                           'launch_time': u'2014-06-06T11:08:08.000Z',
                           'persistent': False,
                           'instance_type': u'm3.large',
                           'root_device_name': u'/dev/sda1',
                           'hypervisor': u'xen',
                           'private_ip_address': u'172.31.45.53',
                           'vpc_id': u'vpc-080bc76d', 'product_codes': []}]



    def test_get_data_region(self):
        """Configuration file"""
        region = get_data_region("us-east-1", datas)
        self.assertEqual("us-east", region['region'])

    def test_get_instance(self):
        """Configuration file"""
        region = get_data_region("us-east-1", datas)
        inst = get_instance("m3.large", region)
        self.assertEqual("2", inst['vCPU'])

    def test_instance_weights(self):
        """
        Compute instance weights
        """
        region = get_data_region("us-east-1", datas)
        result = instance_weights(self.injectors, "us-east-1", datas)
        self.assertEqual({u'i-e78942b5': 12, u'i-7277bf20': 1}, result)

if __name__ == '__main__':
    unittest.main()
