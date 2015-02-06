# -*- coding: utf-8 -*-

import yaml
from os import walk

class YamlLoad():
    def __init__(self, inventory_dir):
        


class Partitionings:
    self.subdir = 'partitioning'
    def __init__(self, inventory_dir):
        pass

class VirtualIps:
    self.subdir = 'virtual-ips'
    def __init__(self, inventory_dir):
        pass

class Hosts:
    self.subdir = 'hosts'
    def __init__(self, inventory_dir):
        pass

class Hardwares:
    self.subdir = 'hardwares'
    def __init__(self, inventory_dir):
        pass


class General:
    self.subdir = 'general'
    def __init__(self, inventory_dir):
        pass

class Inventory:
    def __init__(self, inventory_dir):
        self.hosts          = Hosts(inventory_dir)
        self.general        = General(inventory_dir)
        self.hardwares      = Hardwares(inventory_dir)
        self.partitionings  = Partitionings(inventory_dir)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
