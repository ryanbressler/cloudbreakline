from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.urlfetch import fetch
from django.utils import simplejson as json


class GeneProxy(webapp.RequestHandler):
	def get(self):
		proxyhost = "http://fastbreak.systemsbiology.net/google-dsapi-svc/addama/systemsbiology.org/datasources/tcgajamboree/fastbreak/genes/query?"
		target = proxyhost +self.request.query

		re= fetch(target, headers={ "API_KEY":"952975ec-93c3-44c0-b32a-e68dbafea5ce"})
		
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(re.content)

		

application = webapp.WSGIApplication([('/genedata', GeneProxy)],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()



	


	
