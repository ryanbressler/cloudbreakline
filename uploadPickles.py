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

import sys
import os
import glob
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
try: import cPickle as pickle
except ImportError: import pickle
import urllib2

import poster


def postFile(filename,uploadurl):
	"""Post a file to the uploadurl"""
	print "Uploading %s\n"%(filename)	
	datagen, headers = poster.encode.multipart_encode({"file": open(filename, "r")})
	request = urllib2.Request(uploadurl, datagen, headers)
	urllib2.urlopen(request)

def pickleToByChrJsonandUpload(picklefile,uploadKeyService):
	"""Convert a pickle file to a .json on disk"""
	pfile = open(picklefile)
	index = pickle.load(pfile)
	pfile.close()
	
	for chr in index:
		jsonfile="%s.index.%s.json"%(picklefile[:28],chr)
		jfile = open(jsonfile,"w")
		json.dump(index[chr],jfile)
		jfile.close()				
		uploadUrl = getPostUrl(uploadKeyService)
		postFile(jsonfile,uploadUrl)
		
def getPostUrl(uploadKeyService):
	"""Get the upload key from service provided by the app"""
	uploadUrl = str(json.load(urllib2.urlopen(uploadKeyService)))
	print "Upload url is %s\n"%(uploadUrl)
	return uploadUrl

def main():
	# Register the streaming http handlers with urllib2
	poster.streaminghttp.register_openers()
	
	uploadKeyService = sys.argv[1]
	
	
	for filepatern in sys.argv[2:]:
		for picklefile in glob.glob(filepatern):
			pickleToByChrJsonandUpload(picklefile,uploadKeyService)
			
	


if __name__ == "__main__":
	main()

			
	