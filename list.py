from google.appengine.ext.blobstore import BlobInfo 

blobs = BlobInfo.all()


print 'Content-Type: text/plain'
print ''
for blob in blobs.run():
	print "%s\n"%(blob.filename)