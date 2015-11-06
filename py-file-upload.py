#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 17:46:36 2015

@author: mcontrac
"""

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
from shutil import copyfileobj
from os import chown, chmod, getuid, path as ospath
import cgi, pwd
import cgitb; cgitb.enable(format="text")

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class HeadResponses(object):
    
    # do_GOOD return a HTTP 200 status for success
    # Success is defined as file was copied to the server, even if ownership was not changed.
    def do_GOOD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
    
    # do_BAD return HTTP 400 status for failure or misuse
    def do_BAD(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('This server may only be used for file upload.')
 

class FileUpload(object):
    
    def get_file_data(self, form):
        
        fh = form.getvalue('sfname')
        u = form.getvalue('user')
        g = form.getvalue('group')
        
        # Basic checks for user and group
        if u is None or u == '':
            u = getuid() # Defaults to the user executing this code
        if g is None or g == '':
            g = pwd.getpwuid(u)[3] # Default group of user executing this code
        
        # Checks and prep for writing the file
        fpath, fname = ospath.split(fh)
        if not ospath.isabs(fpath):
            return (False, 400, "Path of filename on server is not absolute")
        if not ospath.isdir(fpath):
            return (False, 400, "Cannot find directory on server to place file")
        
        # Check permissions to write file
        try:
            out = open(fh, 'wb')
        except IOError:
            return (False, 400, "Can't write file at destination. Please check permissions.")
            
        # Write file since everything else succeeded
        out.write(form['file'].file.read())
        
        # Changing access control of file in case chown cannot be executed
        chmod(fh, 0775)
        
        # Only works with sudo or root privileges
        try:
            chown(fh, u, g)
        except:
            return (True, 200, "Could not change owrnership of %s. Please contact server admin." % fh)
        
        return (True, 200, "%s ownership changed to user %s" % (fh, pwd.getpwuid(u)[0]))
    
class PostHandler(CGIHTTPRequestHandler, HeadResponses, FileUpload):
    
    # Disallowing GET requests to prevent misuse
    def do_GET(self):
        self.do_BAD()
    
    # Defining POST request handler
    def do_POST(self):
        f = StringIO()
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
        
        # Check if file is present, and copy to server
        if "file" in form:
            (r, resp, info) = self.get_file_data(form)
            print r, info, "by: ", self.client_address # Log request result and IP of the client
            
            if r:
                f.write("File upload successful: %s" % info) # Return success info to the client
                f.seek(0)
                if resp == 200: 
                    self.do_GOOD()
                else:
                    self.do_BAD
            else:
                f.write("File upload failed: %s" % info) # Return failure info to client
                f.seek(0)
                if resp == 200: 
                    self.do_GOOD()
                else:
                    self.do_BAD
            
            if f:
                copyfileobj(f, self.wfile)
                f.close()
            
        else:
            self.do_BAD() # Error out since no file is available

if __name__ == '__main__':
    httpd = HTTPServer(('', 80), PostHandler) # Runs on localhost port 80. Change the host and prot here
    httpd.serve_forever()