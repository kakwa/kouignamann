# -*- coding: utf-8 -*-
class RelationError(Exception):
    def __init__(self, key, value):
        self.key   = key
        self.value = value

class DumplicatedKey(Exception):
    def __init__(self, host, key):
        self.host   = host
        self.key    = key
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
