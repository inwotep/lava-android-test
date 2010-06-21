import os
import urllib
import urlparse
from subprocess import Popen, PIPE

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    loc = urlpath.rfind('/')
    filename = urlpath[loc+1:]
    if path:
        filename = os.path.join(path,filename)
    urllib.urlretrieve(url, filename)
    return filename

def run_external(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    rc = p.returncode
    return rc,output

def write_file(data,filename):
    fd = open(filename,"w")
    fd.write(data)
    fd.close()

