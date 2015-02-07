# -*- coding: utf-8 -*-

import os
import sys
from yaml.error import *
from yaml.nodes import *
from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.constructor import *
from yaml.resolver import *

import yaml
try:
        from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
        from yaml import Loader, Dumper


class MyLoader(Reader, Scanner, Parser, Composer, Constructor, Resolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self)
        Resolver.__init__(self)

    def construct_mapping(self, node, deep=False):
        exc = sys.exc_info()[1]
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "found unacceptable key (%s)" % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            if key in mapping:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "found dumplicate key (%s)" % key)
            mapping[key] = value
        return mapping


class YamlLoad:

    def mergeNoCollision(self, d1, d2):
        merged = {}
        for d in [ d1, d2 ]:
            for k, v in d.items ():
                if k not in merged:
                    merged [k] = v
                else:
                    raise NameError('Duplicate')
        return merged

    def monkeyYmlLoad(self, stream):
        loader = MyLoader(stream)
        try:
            return loader.get_single_data()
        finally:
            loader.dispose()

    def load(self, inventory_dir, subDir):
        ymlDir = os.path.join(inventory_dir, subDir)
        ymlFiles = []
        inv = {}
        for (dirpath, dirnames, filenames) in os.walk(ymlDir):
            def dirAppend(yml):
                return os.path.join(dirpath, yml)
            ymlFiles.extend(map(dirAppend,filenames))
        for ymlFile in ymlFiles:
            stream = open(ymlFile, 'r')
            content = self.monkeyYmlLoad(stream)
            inv = self.mergeNoCollision(inv, content)
        print inv
        return inv
        
class Partitionings(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'partitionings'
        self.load(inventory_dir, self.subDir)

class VirtualIps(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'virtual-ips'
        self.load(inventory_dir, self.subDir)

class Hosts(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'hosts'
        self.load(inventory_dir, self.subDir)

class Hardwares(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'hardwares'
        self.load(inventory_dir, self.subDir)

class General(YamlLoad):
    def __init__(self, inventory_dir):
        self.subDir = 'general'
        self.load(inventory_dir, self.subDir)

class Inventory:
    def __init__(self, inventory_dir):
        self.hosts          = Hosts(inventory_dir)
        self.general        = General(inventory_dir)
        self.hardwares      = Hardwares(inventory_dir)
        self.virtualIps     = VirtualIps(inventory_dir)
        self.partitionings  = Partitionings(inventory_dir)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
