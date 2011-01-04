#!/usr/bin/env python

"""
__version__ = "$Revision: 0.333 $"
__date__ = "$Date: 2011/01/01 $"
__author__ = "http://www.twitter.com/pengelana"
"""

import re 
import sys
import gzip
import time
import socket
import urllib
import urllib2
import optparse
import cStringIO

def checkURL(url=None):
    r = ''
    pattern = {'idws': r'((?:http://|www\.)?indowebster\.com/\S+)'}
    for p in pattern:
        u = re.compile(pattern[p]).findall(url)
        if u: break
    if u:
        r = u[0]
        if r[0:7] != 'http://':
            r = 'http://' + r
        return r
    else:
        return 0

def gunzip(fileobj=None):
    g = gzip.GzipFile(fileobj=fileobj).read()
    return g

def openURL(opener=None, url=None, data=None):
    maxRet = 4 
    ret = 0
    eRr = ''
    errorStr =  {   'not found'     : 'FILES INDOWEBSTER NOT FOUND',
                    'url error'     : 'URL=error_handler.php?message=',
                    'private file'  : 'File ini merupakan file PRIVATE',
                    'maintenance'   : '<title>Server Maintenance</title>',
                }
    while ret < maxRet:
        try: 
            page = opener.open(url, data)
            if  page.headers.getheader('Location'): 
                if 'error' in page.headers.getheader('Location'):
                    ret += 1
                    if ret ==  maxRet:
                        return 0
                    print "(%s/%s) %s: Static Error %s" % (ret, maxRet - 1, maxRet - ret, page.headers.getheader('Location'))
                    time.sleep(maxRet - ret)
                    continue
            html = page.read()
            if page.headers.getheader("Content-Encoding") == 'gzip':
                html = gunzip(cStringIO.StringIO(html))
            for eStr in errorStr.keys():
                if errorStr[eStr] in html:
                    eRr = eStr
                    break
            if eRr:
                ret += 1
                if ret == maxRet:
                    return 0
                print "(%s/%s) %s: %s %s" % (ret, maxRet - 1, maxRet - ret, eRr.upper(), url)
                eRr = ''
                time.sleep(maxRet - ret)
                continue        
        except urllib2.URLError, e:
            ret += 1 
            if ret ==  maxRet:
                return 0
            print "(%s/%s) %s: %s %s" % (ret, maxRet - 1, maxRet - ret, e, url)
            time.sleep(maxRet - ret)
        else:
            ret = maxRet
    return html, page.headers.items()

def getURL(opener=None, url=None):  
    postval = {}
    postkey = ("kuncis", "id", "name")
    val = None
    postpattern = r'type="hidden" value="([^"]+)" name="%s"'
    t =  r'Original name:\s?</b>\s?(?:<!--INFOLINKS_ON-->)?([^<]+)(?:<!--INFOLINKS_OFF-->)?'
    f = r'<a href="([^"]+)" class="tn_button1">'
    srv = r'(?:http://)?(?:w{1,3}\.)?indowebster.com/[^"<]+'
    domain = '%s//%s/' % (url.split('/')[0], url.split('/')[2])

    (html, header) = openURL(opener, url, data=None)
    if not html: return 0

    title = re.findall(t, html)[0].strip()
  
    nextpage = re.findall(f, html)
    if not nextpage: return 0
    
    (html, header) = openURL(opener, domain + nextpage[0])

    for p in postkey:
        val = re.findall(postpattern % p, html)
        if val:
            postval[p] = val[0]
    
    (html, header) = openURL(opener, domain + 'download.php', urllib.urlencode(postval))
    for item in header:
        if 'refresh' in item[0]:
            return title, item[1].split(';')[1].strip()

    return 0 
            
def main(): 
    cmd = optparse.OptionParser()
    cmd.add_option("-u", "--url", dest="url", help="URL")
    cmd.add_option("-f", "--file", dest="listfile", help="File")
    cmd.add_option("-o", "--out", dest="out")
    cmd.add_option("-d", "--debug", dest="debug", action="store_true", default=False)
    cmd.add_option("-t", "--timeout", type="float", dest="timeout", default=300.0, help="Default Timeout")
    (options, args) = cmd.parse_args()
    download = []
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPHandler(debuglevel=options.debug))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)'), \
        ('Accept-Encoding', 'gzip'),]
    socket.setdefaulttimeout(options.timeout) 
    start = time.time()
    if options.listfile and (options.listfile is not None):
        try:
            listFile = file(options.listfile, 'r')
        except IOError, e:
            print e
            sys.exit(1)
        items = listFile.readlines()
        for item in items:
            i = checkURL(item.strip())
            if i: 
                download.append(i)
    elif options.url:
        i = checkURL(options.url.strip())
        if i: 
            download.append(i)
    else:
        cmd.print_help()
    if options.out: f = open(options.out, "w")
    c = 0
    o = ''
    notFound = []
    for item in download:
        url = getURL(opener, item)
        if url: 
            c += 1
            if url[0]:
                o = " " + "out=" + url[0]
            else:
                o = " " + "out="+ item.split("/")[-1].split(".")[-2] + "." + url[1].split(".")[-1] 
            print url[1]
            print o
            if options.out: 
                f.write(url[1] + "\n" + o + "\n")
        else:
            notFound.append(item)
    stop = time.time()
    print "-" * len(o)
    print "(%s/%s): %.3fs" % (c, len(download), stop - start)
    if notFound:
        print "Error:"
        for n in notFound:
            print n
        print "-" * len(n)

if __name__ == '__main__':
    main()
