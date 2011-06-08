#!/usr/bin/python

import re
import sys
import time
from optparse import OptionParser
from ldtp import *
from urllib import urlopen

chromium_data = {
    "cmd":"chromium-browser",
    "title":"*Chromium",
    "urlfield":"txt0"
}

firefox_data = {
    "cmd":"firefox",
    "title":"*Firefox",
    "urlfield":"txtGotoaWebSite"
}

browser_data = {
    "firefox":firefox_data,
    "chromium":chromium_data
}

site = "http://service.futuremark.com/peacekeeper/run.action"
#site = "http://service.futuremark.com/peacekeeper/results.action?key=5sdG"

try:
    browser = browser_data[sys.argv[1]]
except:
    print "Usage: %s [%s]" % (sys.argv[0], '|'.join(browser_data.keys()))
    sys.exit(1)

closewindow(browser["title"])

launchapp(browser["cmd"], [site])

if not waittillguiexist(browser["title"], guiTimeOut = 60):
    print "Error: Program never started"
    sys.exit(-1)

result_url = gettextvalue(browser["title"], browser["urlfield"])
wait_loop = 60 # 60 * 30 seconds = 15 minutes
time.sleep(10)

while not re.search('results.action', result_url) and wait_loop > 0:
    result_url = gettextvalue(browser["title"], browser["urlfield"])
    print "waiting %d ..."%wait_loop
    time.sleep(30)
    wait_loop = wait_loop-1

closewindow(browser["title"])

print result_url

if wait_loop > 0:
    fd = urlopen(result_url)
    data = fd.read()
    fd.close()

    scoreline = re.search('<div class="score">(\d+)</div>', data)
    if scoreline:
        score = scoreline.group(1)
    print "pass: Score = %s" % score
else:
    print "fail: Score = 0"
