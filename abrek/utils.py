import os
import urllib
from subprocess import Popen, PIPE

def geturl(url, path=""):
    loc = url.rfind('/')
    filename = url[loc+1:]
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

