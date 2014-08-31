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
    nr_total = 0
    crawler = Crawler()
    while True:
        search = raw_input('1) BFS\n2) DFS\nSelect search type [1 - 2]: ')
        if search == '1': 
            search = 'BFS' 
        elif search == '2': 
            search = 'DFS' 
        else: 
            continue
        url = raw_input('Enter url to crawl [0 to exit]: ')
        if search == '0' or url == '0':
            print 'Exiting...'
            return False
        else:
            print 'Search: {}'.format(search)
            if crawler.crawl(url, output=True, search=search):
                nr_total += crawler.nr
                print '\n%d sites crawled.' % crawler.nr
                print 'A total of %d sites have been crawled.\n' % nr_total
            else:
                print 'Already crawled or uncrawable. Try again. \n'



if __name__ == '__main__':
    main()
