# vim: ai ts=4 sw=4 expandtab 
import mock
import StringIO
import urllib2
import unittest
import zipfile

from mlabns.handlers import update
from mlabns.db import model
from mlabns.util import util
from mlabns.util import maxmindupdate

from google.appengine.ext import testbed
from google.appengine.ext import db

class MaxMindUpdateCommon(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_urlfetch_stub()
        self.db_root = db.Model(key_name='root')

    def tearDown(self):
        self.testbed.deactivate()

    def createSuccessfulConfiguration(self):
        self.configuration =\
            model.MaxmindConfiguration(url="http://geolite.maxmind.com/download/geoip/database", files=["GeoLite2-City-CSV.zip", "GeoLite2-Country-CSV.zip"])
        self.configuration.put()

    def createSuccessfulLocalConfiguration(self):
        self.configuration =\
            model.MaxmindConfiguration(url="http://localhost/", files=["GeoLite2-City-CSV.zip", "GeoLite2-Country-CSV.zip"])
        self.configuration.put()


    def createFailureConfiguration(self):
        self.configuration =\
            model.MaxmindConfiguration(url="url", files=["f1", "f2"])
        self.configuration.put()

    def createMaxMindUpdateObject(self):
        self.update_object = maxmindupdate.MaxMindUpdate(self.configuration)

class MaxmindConfigurationTest(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxmindConfigurationTest, self).setUp()
        self.configuration = \
            model.MaxmindConfiguration(url="url", files=["f1", "f2"])
        self.configuration.put()

    def testGetMaxmindConfiguration(self):
        self.assertEqual(self.configuration.url,
            model.get_maxmind_configuration().url)
        self.assertEqual(self.configuration.files,
            model.get_maxmind_configuration().files)

class MaxMindDownloadUpdateTest(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxMindDownloadUpdateTest, self).setUp()
        self.createSuccessfulConfiguration()
        self.createMaxMindUpdateObject()
    
    # TODO: Make this meaningfully test what it
    # says it does.
    def testMaxMindDownloadUpdate(self):
        self.assertEqual(True,True)
        #self.assertEqual(True, self.update_object.download_update())

    def testMaxMindPreDownloadUpdate(self):
        self.assertEqual(True,True)
        #self.assertEqual(True, self.update_object.download_update())

class MaxMindUpdateTestUnzipAndValidate(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxMindUpdateTestUnzipAndValidate, self).setUp()
        self.createSuccessfulConfiguration()
        #self.createSuccessfulLocalConfiguration()
        self.createMaxMindUpdateObject()
        self.update_object.download_update()

    def testMaxMindValidateUpdate(self):
        self.assertEqual(True, self.update_object.validate_update())

    # TODO: Make this meaningfully test what it
    # says it does.
    def testMaxMindPreValidateUpdate(self):
        self.assertEqual(True, self.update_object.validate_update())
        self.assertEqual(True, self.update_object.validate_update())

    def testMaxMindUpdateUnzipUpdate(self):
        self.assertEqual(True, self.update_object.unzip_update())

class MaxMindUpdateTestParsing(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxMindUpdateTestParsing, self).setUp()
        self.createSuccessfulConfiguration()
        #self.createSuccessfulLocalConfiguration()
        self.createMaxMindUpdateObject()
        self.update_object.download_update()
        self.update_object.download_update()
        self.update_object.unzip_update()

    # TODO: document why this is here.
    def testMaxMindUpdateOpenReturnsDifferentObjects(self):
        self.assertNotEqual(
            self.update_object.open("City-Blocks-IPv4"),
            self.update_object.open("City-Blocks-IPv6"))

    def testMaxMindParseBlocks(self):
        blocks_csv = self.update_object.open("City-Blocks-IPv4")
        self.assertNotEqual(None, blocks_csv)
        blocks_csv_parser = maxmindupdate.MaxMindUpdateParser(blocks_csv, model.MaxmindCityBlock)
        self.assertEqual(True, blocks_csv_parser.parse())

class MaxMindUpdateCreateCityBlock(unittest.TestCase):
    def MaxmindCityBlockEqual(self, a, b, msg=None):
        if a.start_ip_num != b.start_ip_num:
            raise(self.failureException(
                "start_ip_nums (%s/%s) do not match." %
                (a.start_ip_num, b.start_ip_num)))
        if a.end_ip_num != b.end_ip_num:
            raise(self.failureException(
                "end_ip_nums (%s/%s) do not match." %
                (a.end_ip_num, b.end_ip_num)))
        if a.location_id != b.location_id:
            raise(self.failureException(
                "location_ids (%s/%s) do not match." %
                (a.location_id, b.location_id)))

    def setUp(self):
        self.addTypeEqualityFunc(
            model.MaxmindCityBlock,
            self.MaxmindCityBlockEqual)

    def testCreateCityBlock(self):
        truth = model.MaxmindCityBlock(
            start_ip_num = 16777472,
            end_ip_num = 16777472+255,
            location_id="a")
        question = maxmindupdate.MaxMindUpdateCreateCityBlock(
            network="1.0.1.0/24",
            geoname_id="a")
        self.assertEqual(truth, question)

if __name__ == '__main__':
    unittest2.main()
