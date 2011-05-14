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
import time

startclock = time.clock()
starttime = time.time()

import os, glob
import cgi
import cgitb
cgitb.enable()
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
#try: import cPickle as pickle
#except ImportError: import pickle
import sys
import math
#import urllib2
#import bisect
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import memcache

import logging
#from config import *


globalIndexStore = {}


def log(msg):
	#logf = open(logfile,"a")
	logging.info("%s:\t%s\n"%(time.strftime("%c"), msg))
	#logf.close()
	
def googleDataTable(cols,rows):
	out = {"cols":[],"rows":[]}
	
	for col in cols:
		out["cols"].append({"id":col,"type":"string"})
	for row in rows:
		rowout = []
		for val in row:
			rowout.append({"v":val})
		out["rows"].append({"c":rowout})
	return out


#reimplementations of bisect.bisect_left and bisect.bisect_right for breakpoint data
def bisect_left(a, x, lo=0, hi=None):

	if lo < 0:
		raise ValueError('lo must be non-negative')
	if hi is None:
		hi = len(a)
	while lo < hi:
		mid = (lo+hi)//2
		if int(a[mid]["Pos1"]) < x: lo = mid+1
		else: hi = mid
	return lo		

def bisect_right(a, x, lo=0, hi=None):

	if lo < 0:
		raise ValueError('lo must be non-negative')
	if hi is None:
		hi = len(a)
	while lo < hi:
		mid = (lo+hi)//2
		if x < int(a[mid]["Pos1"]): hi = mid
		else: lo = mid+1
	return lo

#apply a series of filters to our input, returning the derived data set
def filter(filename,chrm,start,end,filters):
	out = []
	
	indexname = "%s.index.%s.json"%(filename,chrm)
	log("attempting to load from m cache")
	index = memcache.get(indexname)
	if index is None:
		log("mcache loading failed, loading from blobstore")
		blob = BlobInfo.gql("where filename = '%s'"%(indexname)).get()
		if not blob is None:
			log("mcache loading failed, parseing from json")
			index = json.load(blob.open())
			log("adding to memcache")
			try:
				if not memcache.add(indexname, index):
					logging.error("Memcache set failed.")
			except ValueError:
				logging.info("Memcache value error.")
	
	if not index is None:
		leftbound = bisect_left(index,start)
		rightbound = bisect_right(index,end)                
		for edge in index[leftbound:rightbound]:
			#if edge < start:
			#	continue
			#if edge["Pos1"] > end:
			#	break
				
			includeme = False
			if filters != False:
				for filter in filters:
					if	edge["Type"]==filter["type"] and int(edge["Score"])>=int(filter["minscore"]) :
						includeme = True
						break
			else:
				includeme = True
			if includeme==True:
				out.append(edge)
	return out

#grow the tree in a method similar to a depth first search
def growDepthFirst(chrm,start,end,index,curdepth, maxdepth,radius,adjList,visited):
	curdepth+=1
	if curdepth >= maxdepth:
		return
	
	for edge in filter(index,chrm,start,end):
		if edge["line"] in visited:
			continue
		adjList.append([edge["line"],edge["Chr1"],edge["Chr2"],"%i"%(edge["Pos1"]),"%i"%(edge["Pos2"]),"%i"%(edge["num_Reads"]),edge["Type"],edge["Score"]])
		visited[edge["line"]]=True
		growDepthFirst(edge["Chr2"],edge["Pos2"]-radius,edge["Pos2"]+radius,index,curdepth, maxdepth,radius,adjList,visited)
	
def main():
	log("Script called with uri: \"%s\""%(os.environ.get("REQUEST_URI")))
	form=cgi.FieldStorage()
	
	for field in form:
		log("paramater %s is \"%s\""%(field,form.getvalue(field)))
	
	chrm = str(form.getvalue("chr"))	#the chromosone the start region is located on
	start = int(form.getvalue("start")) #the start of the start region
	end = int(form.getvalue("end"))	#the end of the start region
	searchdepth = int(form.getvalue("depth"))	#the depth of transversals to follow
	searchradius = int(form.getvalue("radius"))  #the size of leaves
	bdoutfile = str(form.getvalue("file"))  #the breakdancer output
	filters = form.getvalue("filters")
	key = str(form.getvalue("key"))
	
	if filters == None:
		filters = False
	else:
		filters = json.loads(str(filters)) 
	
	##### google datasource code; could be refactored
	reqId=0
	responseHandler="google.visualization.Query.setResponse"
	tqx=str(form.getvalue("tqx")) #the google query
	for param in tqx.split(";"):
		pair = param.split(":")
		if pair[0] == "reqId":
			reqId = int(pair[1])
		if pair[0] == "responseHandler":
			responseHandler = int(pair[1])
			
	
	
	
	
	
	#Variable to hold an adjacancy list of the directed acyclic(?) graph representing the tree
	#each row should have  elements:
	outcols = ["edge_id", "source_chr", "target_chr", "source_pos", "target_pos", "num_reads","type","score"]
	
	adjList = []
	
	#variable to hold the regions that have allready been searched
	visited = {}
	
	index = {}
	
	loadstart = time.time()
	
	# if(loadPickleFromUri==True):	
	# 	target = picklehost + bdoutfile
	# 	log("Loading %s from jcr"%(target))
	# 	req = urllib2.Request(target, None, { "API_KEY":key})
	# 	response = urllib2.urlopen(req)	
	# 	index = pickle.loads(response.read())
	# else:
	# 	log("Loading %s from filesystem"%(bdoutfile))
	# 	indexfile = open(os.path.join(datapath,bdoutfile.lstrip("\/")),"r")
	# 	index = pickle.load(indexfile)
	# 	indexfile.close()
	
# 	log("attempting to load from m cache")
# 	index = memcache.get(bdoutfile)
# 	if index is None:
# 		log("mcache loading failed, loading from blobstore")
# 		blob = BlobInfo.gql("where filename = '%s'"%(bdoutfile)).get()
# 		log("mcache loading failed, parseing from json")
# 		index = json.load(blob.open())
# 		log("adding to memcache")
# #		if not memcache.add(bdoutfile, index, 120):
# #			logging.error("Memcache set failed.")

#	if not bdoutfile in globalIndexStore:
#		blob = BlobInfo.gql("where filename = '%s'"%(bdoutfile)).get()
#		globalIndexStore[bdoutfile]=json.load(blob.open())
#	index=globalIndexStore[bdoutfile]
	
	
	
		
	
	
	log("Loading took %s real seconds."%(time.time()-loadstart))	
	log("Index has chrs: %s"%(", ".join(index.keys())))
	
	#growDepthFirst(chrm,start,end,index,0,searchdepth,searchradius,adjList,visited)
	log("Starting depth first search")
	contigs = [[{"chr":chrm,"start":start,"end":end}]]
	for depth in range(searchdepth):
		newcontigs = []
		for contig in contigs[depth]:
			for edge in filter(bdoutfile, contig["chr"],contig["start"],contig["end"],filters):
				if edge["line"] in visited:
					continue
				adjList.append([edge["line"],edge["Chr1"],edge["Chr2"],"%i"%(edge["Pos1"]),"%i"%(edge["Pos2"]),"%i"%(edge["num_Reads"]),edge["Type"],edge["Score"]])
				visited[edge["line"]]=True
				addcontig = True
				chr2 = edge["Chr2"]
				s = edge["Pos2"]-searchradius
				e = edge["Pos2"]+searchradius
				for c in newcontigs:			
					if (chr2 == c["chr"] and ( (s >= c["start"] and s <= c["end"]) or (e >= c["start"] and e <= c["end"]) or (s <= c["start"] and e >= c["end"]))):
						addcontig = False
						if (s < c["start"]):
							c["start"] = s
						if (e > c["end"]):
							c["end"] = e
						break
		
				if addcontig==True:
					newcontigs.append({"chr":chr2,"start":s,"end":e})
	
				
			
		contigs.append(newcontigs);
		
	log("Printing output adj list has %i elements"%(len(adjList)))
	##### google datasource code; could be refactored
	print "Content-type: text/html"
	print
	print "%(responseHandler)s({status:'ok',table:%(table)s,reqId:'%(reqId)i'})"%{'table':json.dumps(googleDataTable(outcols,adjList)),'reqId':reqId,'responseHandler':responseHandler}
	
	log("Done. Request took %s real time %s system time. Exiting Now."%(time.time()-starttime,time.clock()-startclock))

if __name__ == "__main__":
    main()
