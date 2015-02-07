# -*- coding: utf-8 -*-

import os
import sys
from pyyamlwrapper import loadNoDump
from errors import RelationError, DumplicatedKey

class YamlLoad:

    def mergeNoCollision(self, d1, d2):
        merged = {}
        for d in [ d1, d2 ]:
            for k, v in d.items ():
                if k not in merged:
                    merged [k] = v
                else:
                    raise DumplicatedKey(k, self.subDir)
        return merged

    def load(self):
        ymlDir = os.path.join(self.inventory_dir, self.subDir)
        ymlFiles = []
        inv = {}
        for (dirpath, dirnames, filenames) in os.walk(ymlDir):
            def dirAppend(yml):
                return os.path.join(dirpath, yml)
            ymlFiles.extend(map(dirAppend,filenames))
        for ymlFile in ymlFiles:
            stream = open(ymlFile, 'r')
            content = loadNoDump(stream)
            inv = self.mergeNoCollision(inv, content)
        return inv
        
class Partitionings(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'partitionings'
        self.inventory_dir = inventory_dir

class VirtualIps(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'virtual-ips'
        self.inventory_dir = inventory_dir

class Hosts(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'hosts'
        self.inventory_dir = inventory_dir

class Hardwares(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'hardwares'
        self.inventory_dir = inventory_dir

class General(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'general'
        self.inventory_dir = inventory_dir

class Inventory:
    def __init__(self, inventory_dir):
        self.hostsObj          = Hosts(inventory_dir)
        self.generalObj        = General(inventory_dir)
        self.hardwaresObj      = Hardwares(inventory_dir)
        self.virtualipsObj     = VirtualIps(inventory_dir)
        self.partitioningsObj  = Partitionings(inventory_dir)
        self.load()

    def checkRelation(self, hosts, subinv, key):
        for host in hosts:
            if not hosts[host][key] in subinv:
                raise RelationError(host, key)

    def load(self):
        tmp_hosts          = self.hostsObj.load()
        tmp_general        = self.generalObj.load()
        tmp_hardwares      = self.hardwaresObj.load()
        tmp_virtualips     = self.virtualipsObj.load()
        tmp_partitionings  = self.partitioningsObj.load()
        self.checkRelation(tmp_hosts, tmp_hardwares, 'hardware')
        self.checkRelation(tmp_hosts, tmp_partitionings, 'partitioning')
        self.hosts         = tmp_hosts
        self.general       = tmp_general
        self.hardwares     = tmp_hardwares
        self.virtualips    = tmp_virtualips
        self.partitionings = tmp_partitionings

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
