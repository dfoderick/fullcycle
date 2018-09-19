import unittest
import datetime
import backend.fcmutils as utils
import messaging.schema as schema

class TestUtilityFunctions(unittest.TestCase):
    def test_safe_string_null(self):
        nullstring = utils.safestring(None)
        self.assertFalse(nullstring)

    def test_safe_string_other(self):
        astring = utils.safestring(b'test')
        self.assertTrue(astring)

    def test_formattime(self):
        s = utils.formattime(datetime.datetime.now())
        self.assertTrue(s)

    def test_deserializelist(self):
        thelist = ['{"miner_type":"test", "minerid":"test"}']
        s = utils.deserializelist_withschema(schema.MinerInfoSchema(), thelist)
        self.assertTrue(len(s) > 0)

    def test_deserializelist_string(self):
        thelist = ['{"miner_type":"test", "minerid":"test"}']
        s = utils.deserializelistofstrings(thelist, schema.MinerInfoSchema())
        self.assertTrue(len(s) > 0)
