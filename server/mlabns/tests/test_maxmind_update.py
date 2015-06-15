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

want_local_configuration = True

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
        if want_local_configuration == True:
            self.configuration = model.MaxmindConfiguration(
                url="http://localhost/",
                files=["GeoLite2-City-CSV.zip", "GeoLite2-Country-CSV.zip"])
        else:
            self.configuration = model.MaxmindConfiguration(
                url="http://geolite.maxmind.com/download/geoip/database",
                files=["GeoLite2-City-CSV.zip", "GeoLite2-Country-CSV.zip"])
        self.configuration.put()

    def createFailureConfiguration(self):
        self.configuration = model.MaxmindConfiguration(
            url="url",
            files=["f1", "f2"])
        self.configuration.put()

    def createMaxMindUpdateObject(self):
        self.update_object = maxmindupdate.MaxMindUpdate(self.configuration)

class MaxmindConfigurationTest(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxmindConfigurationTest, self).setUp()
        self.configuration = model.MaxmindConfiguration(
            url="url",
            files=["f1", "f2"])
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
    
    def testMaxMindDownloadUpdate(self):
        self.assertEqual(True, self.update_object.download_update())

    # TODO: Make this meaningfully test what it
    # says it does.
    def testMaxMindPreDownloadUpdate(self):
        self.assertEqual(True, self.update_object.download_update())
        self.assertEqual(True, self.update_object.download_update())

class MaxMindUpdateTestUnzipAndValidate(MaxMindUpdateCommon):
    def setUp(self):
        super(MaxMindUpdateTestUnzipAndValidate, self).setUp()
        self.createSuccessfulConfiguration()
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

if __name__ == '__main__':
    unittest2.main()
