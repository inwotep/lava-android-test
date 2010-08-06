import shutil
import os
import urllib2
import urlparse

_fake_files = None

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

def write_file(data, path):
    with open(path, "w") as fd:
        fd.write(data)

def read_file(path):
    global _fake_files
    if _fake_files is not None:
        if path in _fake_files:
            return _fake_files[path]
    with open(path) as fd:
        data = fd.read()
    return data

def fake_file(path, data):
    """
    Set up a fake file to be read with read_file() in testing
    """
    global _fake_files
    if _fake_files is None:
        _fake_files = {}
    _fake_files[path] = data
