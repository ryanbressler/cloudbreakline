from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from django.utils import simplejson as json


class MainPage(webapp.RequestHandler):
	def get(self):
		upload_url = blobstore.create_upload_url('/upload')
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(json.dumps(upload_url))

	
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key()) #todo: change this
		

application = webapp.WSGIApplication([('/uploadkey', MainPage),('/upload', UploadHandler)],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()