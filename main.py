#!/usr/bin/env python
#-*- coding: utf-8 -*-

from pycrawler import Crawler
import sys


def main():
    """
    Example usages
    """
    url = ''
    nr = 0
    crawler = Crawler()
    while True:
        url = raw_input('Enter url to crawl [0 to exit]: ')
        if url == '0':
            print 'Exiting...'
            return False
        else:
            nr = crawler.crawl(url, output=True)
            print '\nA total of %s sites crawled.\n' % str(nr)



if __name__ == '__main__':
    main()