from django import test
from localground.apps.site.views import uploader
from localground.apps.site import models
from localground.apps.site.tests import ViewMixin
from rest_framework import status
import urllib

class UploadTest(test.TestCase, ViewMixin):

    def setUp(self):
        ViewMixin.setUp(self)
        self.urls = ['/upload/']
        self.view = uploader.init_upload_form
