#!/usr/bin/env python

"""
__version__ = '0.01c'
__author__ = 'http://twitter.com/pengelana'
__license__ = 'GPL'
"""

import re
import os
import sys
import urllib2

def main():
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=False))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)')]

    google = "http://www.google.com/"
    m = 'http://www.google.com/logos/'
    p = opener.open(m + 'index.html')
    html = p.read()

    years = []
    ytd = re.compile('<li>(\d{4})</ul>').findall(html)
    years = re.compile('<a href="([^"]+)">(\d{4})</a>').findall(html)
    if not ytd:
        sys.exit(1)

    if years:
        years.reverse()
        years.insert(0, ('index.html', ytd[0]))

    print "%s year(s)" % len(years)
    for year in years:
        print year[1]
        if year[1] != ytd[0]:
            p = opener.open(m + year[0])
            html = p.read()

        months = []
        mtd = re.compile('<li>([a-z]{3}-[a-z]{3})', re.IGNORECASE).findall(html)
        months = re.compile('<li><a href="([^"]+)">([a-z]{3}-[a-z]{3})</a>', re.IGNORECASE).findall(html)

        if not mtd:
            sys.exit(1)

        months.reverse()
        months.insert(0, ('index.html', mtd[0]))

        for month in months:
            if month[1] != mtd[0]:
               p = opener.open(m + month[0])
               html = p.read()
            logos = re.compile('(?:src="|url\()(/[^"\)]+)(?:"|\))\s(?:title|no-repeat|style="border)').findall(html)
            dts = re.compile('<dt>([a-z]{3} \d{1,2})', re.IGNORECASE).findall(html)
            titles = re.compile('id="[^"]+">([^\n]+)').findall(html)
            title = ''
            path = year[1] + '/' + month[1]
            if logos:
                if not os.path.exists(path):
                    os.makedirs(path)
            print " " + month[1] + " " + "(" + str(len(logos)) + ")"
            for counter in range(0, len(logos)):
                title = re.sub('<[^>]+>', '',titles[counter]).strip().replace('/', '-')
                print "  " + dts[counter] + " - " + title,
                lf = path + '/' + dts[counter] + "-" + title + "_" + str(counter) + "_" + logos[counter].split('/')[-1]
                p = opener.open(google.rstrip('/') + logos[counter])
                if os.path.exists(lf):
                    if p.headers.getheader('content-length'):
                        if long(p.headers.getheader('content-length')) == os.path.getsize(lf):
                            print "(!)"
                            continue
                print "(*)"
                img = p.read()
                f = open(lf, "wb")
                f.write(img)
                f.close()

if __name__ == "__main__":
    main()