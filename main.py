#!/usr/bin/env python
#-*- coding: utf-8 -*-

from pycrawler import crawl
import sys


def main():
	"""
	Example usages
	"""
	url = ''
	if not len(sys.argv) > 1:
		print 'Use URL as argument.'
		sys.exit(0)
	url = sys.argv[1]
	crawl(url, output=True)

	with open('data.txt') as textfile:
		print '\n\n\n' + textfile.read(),


if __name__ == '__main__':
	main()