from google.appengine.ext import blobstore
from django.utils import simplejson as json


upload_url = blobstore.create_upload_url('/upload')

print 'Content-Type: text/plain'
print 
print json.dumps(upload_url)