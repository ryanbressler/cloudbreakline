#!/usr/bin/python
#
# 
#     Copyright (C) 2003-2010 Institute for Systems Biology
#                             Seattle, Washington, USA.
# 
#     This library is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 2.1 of the License, or (at your option) any later version.
# 
#     This library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public
#     License along with this library; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
# 
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