import shutil
import os
import urllib2
import urlparse

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path,filename)
    fd = open(filename, "w")
    try:
        response = urllib2.urlopen(url)
        fd = open(filename, 'wb')
        shutil.copyfileobj(response,fd,0x10000)
        fd.close()
        response.close()
    except:
        raise RuntimeError("Could not retrieve %s" % url)
    return filename

def write_file(data,path):
    with open(path, "w") as fd:
        fd.write(data)

