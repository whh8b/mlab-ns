# vim: ai ts=4 sw=4 expandtab 
from google.appengine.api import urlfetch
from google.appengine.ext import db

from mlabns.db import model
from mlabns.third_party import ipaddr
from mlabns.util import constants

import logging
import socket
import string

import StringIO
import hashlib
import zipfile

class MaxMindUpdate(object):
    def __init__(self,configuration):
        self.configuration = configuration

        self.zipped_updates = None
        self.raw_updates = None
        self.unzipped_updates = None
        self.download_status = None

        self.validated_status = None

    def download_update(self):
        if self.download_status != None:
            logging.warning("Predownloaded; returning early")
            return self.download_status

        url = self.configuration.url
        files = self.configuration.files
        self.zipped_updates = {}
        self.raw_updates = {}
        for f in files:
            self.raw_updates[f] = self._download_update_file(url, f)
            # We have to make a copy here. If we do not,
            # the zipfile.ZipFile constructor changes
            # the state of the object and it causes problems
            # when we validate.
            self.zipped_updates[f] =\
                zipfile.ZipFile(\
                StringIO.StringIO(self.raw_updates[f].getvalue()))
        # Now, check if all the zipped updates were
        # properly downloaded.
        self.download_status = True 
        for f in self.zipped_updates:
            if f == None:
                self.download_status = False
                break
        return self.download_status
   
    def validate_update(self):
        if self.download_status == None or self.download_status == False:
            return False
        if self.validated_status != None:
            logging.warning("Pre validated; returning early.")
            return self.validated_status

        url = self.configuration.url
        files = self.configuration.files
        self.validated_status = True

        # TODO: There might be an easier way to do this.
        for f in files:
            hash = hashlib.new("md5")
            for i in self.raw_updates[f]:
                hash.update(i)
            logging.warning("calculated hash: %s" % str(hash.hexdigest()))
            if hash.hexdigest() != self._download_update_file_md5(url, f):
                self.validated_status = False
                break

        # We cannot clear the raw memory yet.
        # We will need it to unzip the objects.
        # See below for the reason why.
        return self.validated_status

    def unzip_update(self):
        if self.zipped_updates == None:
            return False

        self.unzipped_updates = {}
        # First, make a dictionary whose
        # keys are archive member names.
        # Set the value for each archive
        # member to be the file they are from.
        for f, zf in self.zipped_updates.items():
            for n in zf.namelist():
                self.unzipped_updates[n] = f
        #logging.warning("archive members:%s"%str(self.unzipped_updates.items()))

        # Second, actually unzip them.
        for f in self.unzipped_updates:
            # This many reconstructions is necessary because
            #https://docs.python.org/2/library/zipfile.html#zipfile.ZipFile.open
            # (second Note)
            self.unzipped_updates[f] =\
                zipfile.ZipFile(\
                    StringIO.StringIO(\
                        self.raw_updates[self.unzipped_updates[f]].getvalue()\
                        )\
                    )\
                .open(f)
        logging.warning("archive members:%s"%str(self.unzipped_updates.items()))

        # NOW, we can really clear out the raw contents.
        for f in self.raw_updates:
            self.raw_updates[f].close()
        self.raw_updates = []
        return True

    def open(filename):
        pass

    def _download_update_file_md5(self, url, f):
        try:
            downloaded_md5 = urlfetch.fetch(url + "/" + f + ".md5")
            logging.warning("downloaded hash: %s" % str(downloaded_md5.content))
            return downloaded_md5.content 
        except Exception as e:
            logging.error("ERROR: Could not download Maxmind MD5: %s", str(e))
            return ""

    def _download_update_file(self, url, f):
        try:
            downloaded_file = urlfetch.fetch(url + "/" + f)
            return StringIO.StringIO(downloaded_file.content)
        except Exception as e:
            logging.error("ERROR: Could not download Maxmind update: %s",str(e))
            return None
