#!/usr/bin/env python
#-*- coding: utf-8 -*-

from pycrawler import crawl
import sys


def main():
	url = ''
	if not len(sys.argv) > 1:
		print 'Use URL as argument.'
		sys.exit(0)
	url = sys.argv[1]
	crawl(url)



if __name__ == '__main__':
	main()