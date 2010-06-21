import os
import urllib
import urlparse

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    loc = urlpath.rfind('/')
    filename = urlpath[loc+1:]
    if path:
        filename = os.path.join(path,filename)
    urllib.urlretrieve(url, filename)
    return filename

def write_file(data,path):
    with open(path, "w") as fd:
        fd.write(data)

