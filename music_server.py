#!/usr/bin/python
import cherrypy
import cgi
import tempfile
import os
import subprocess

class PlaySong:

    def __init__(self,songtitle,vol_index):
        if ("mp3" not in songtitle) and ("m4a" not in songtitle) and ("wav" not in songtitle):
            print "***",songtitle
            self.title = "/home/pi/music/105_kreeshte_sarvadikari.mp3"
            print "*** is changed to ",self.title
	    self.volume_level = 100
        else:
            self.title = songtitle
	    self.volume_level=int(vol_index)*100
	self.process=None


    def play(self):
	self.stop()
        if os.name == 'posix':
            print os.name
	    self.process = subprocess.Popen(["omxplayer","--vol",str(self.volume_level), self.title])
        else :
            print self.title
   
    def stop(self):
	if self.process != None:
	  if self.process.poll() == True:
		self.process.terminate()


class myFieldStorage(cgi.FieldStorage):
    """Our version uses a named temporary file instead of the default
    non-named file; keeping it visibile (named), allows us to create a
    2nd link after the upload is done, thus avoiding the overhead of
    making a copy to the destination filename."""

    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()




def noBodyProcess():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)


class fileUpload:
    """fileUpload cherrypy application"""

    @cherrypy.expose
    def index(self):
        """Simplest possible HTML file upload form. Note that the encoding
        type must be multipart/form-data."""

        return """
            <html>
            <body>
                <form action="upload" method="post" enctype="multipart/form-data">
                    File: <input type="file" name="theFile"/>
                     <br/>
                    <input type="submit"/>
                </form>
            </body>
            </html>
            """

    @cherrypy.expose
    def list(self):
        """Simplest possible HTML file upload form. Note that the encoding
        type must be multipart/form-data."""
        #dir_list="C:\\Users\\bhanu\\Music\\iTunes\\iTunes Media\\Music\\"
        dir_list=cherrypy.config.get("dir_list")
        str="<form action='playsonglist' method='post' enctype='multipart/form-data'>" 
        str+="<table>"
        str+="<th> check </th><th> Songs </th>"
        for r,d,f in os.walk(dir_list):
            for file in f:
                if "mp3" in file or "m4a" in file or "wav" in file:
                    str+= '''<tr><td><input type="checkbox" name="songsplay[]" value="{0}"></td><td>{1}</td></tr>'''.format(os.path.join(r, file),os.path.join(file))

        str+="</table>"
	str+= """<input type="range" name="points" min="-10" max="10">"""
        str+= """ <input type="submit"/>
                </form> """
        str = """ <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                    }
                    </style>"""+str
        return str

    @cherrypy.expose
    def dropdown(self):
        dir_list=cherrypy.config.get("dir_list")
        str="<form action='playsong' method='post' enctype='multipart/form-data'>" \
            """<select  name="droplist" >"""
        for r,d,f in os.walk(dir_list):
            for file in f:
                if "mp3" in file or "m4a" in file or "wav" in file : # or "m4a" in file or "wav" in file:
                    str+= """ <option value="{0}">{1}</option>""".format(os.path.join(r, file),os.path.join(file))
        str+="</select>"
	str+= """<input type="range" name="points" min="-10" max="10">"""
        str+= """ <input type="submit"/>
                </form> """
        return str

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def playsong(self, filename=None):
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val
       # print lcHDRS
        formFields = myFieldStorage(fp=cherrypy.request.body,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)
        params = {}
        for key in formFields.keys():
            params[ key ] = formFields[ key ].value
        fname = params[ 'droplist']
	range_val = params[ 'points']
	print range_val,"************************"
        print fname
        ps = PlaySong(fname,range_val)
        ps.play()
        return "playing song : <b>"+ fname+"</b>"

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def playsonglist(self, filename=None):
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val
       # print lcHDRS
        formFields = myFieldStorage(fp=cherrypy.request.body,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)
        params = {}
	print formFields.keys
        #for key in formFields.keys():
        #    params[ key ] = formFields[ key ].value
        #fname = params[ 'songsplay']
	#range_val = params[ 'points']
	#print range_val,"************************"
        #print fname
        #ps = PlaySong(fname,range_val)
        #ps.play()
        #return "playing song : <b>"+ fname+"</b>"

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def upload(self, theFile=None):
        """upload action
        We use our variation of cgi.FieldStorage to parse the MIME
        encoded HTML form data containing the file."""

        # the file transfer can take a long time; by default cherrypy
        # limits responses to 300s; we increase it to 1h
        cherrypy.response.timeout = 3600

        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.iteritems():
            lcHDRS[key.lower()] = val

        # at this point we could limit the upload on content-length...
        # incomingBytes = int(lcHDRS['content-length'])

        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = myFieldStorage(fp=cherrypy.request.rfile,
                                    headers=lcHDRS,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)

        # we now create a 2nd link to the file, using the submitted
        # filename; if we renamed, there would be a failure because
        # the NamedTemporaryFile, used by our version of cgi.FieldStorage,
        # explicitly deletes the original filename
        theFile = formFields['theFile']

        print os.path.abspath(theFile.filename)
        if os.name <> "nt":
            os.link(theFile.file.name, '/tmp/'+theFile.filename)
        return "ok, got it filename='%s'" % theFile.filename


# remove any limit on the request body size; cherrypy's default is 100MB
# (maybe we should just increase it ?)
cherrypy.server.max_request_body_size = 0

# increase server socket timeout to 60s; we are more tolerant of bad
# quality client-server connections (cherrypy's defult is 10s)
#cherrypy.config.update('/home/pi/app.conf')
cherrypy.config.update('./app.conf')
cherrypy.quickstart(fileUpload())
