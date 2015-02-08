#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import unicode_literals

import pytest
import sys
import kouignamann
from kouignamann.errors import DumplicatedKey, RelationError


class TestError(object):

    def testDumplicateKeyOneFile(self):
        try:
            inv = kouignamann.Inventory('./tests/inventories/duplicateKeyOneFile')
        except DumplicatedKey:
            return
        else:
            raise AssertionError("expected an exception")

    def testDumplicateKeyMultiFile(self):
        try:
            inv = kouignamann.Inventory('./tests/inventories/duplicateKeyMultiFiles')
        except DumplicatedKey:
            return
        else:
            raise AssertionError("expected an exception")



    def testMissingRelationPartition(self):
        try:
            inv = kouignamann.Inventory('./tests/inventories/missingRelationPartitioning')
        except RelationError:
            return
        else:
            raise AssertionError("expected an exception")



    def testMissingRelationHardware(self):
        try:
            inv = kouignamann.Inventory('./tests/inventories/missingRelationHardware')
        except RelationError:
            return
        else:
            raise AssertionError("expected an exception")


