import os
import urllib
import urlparse

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path,filename)
    urllib.urlretrieve(url, filename)
    return filename

def write_file(data,path):
    with open(path, "w") as fd:
        fd.write(data)

