#!/bin/env python3
import itertools
import optparse
import re
import sys

parser = optparse.OptionParser()
parser.add_option("-d", "--delay", action="append", dest="delays", type="int", default=[])
(opts, args) = parser.parse_args()

input  = open(args[0])
caches = [open(cache) for cache in args[1:]]

cache_re = re.compile(r'(?P<sym>\S*)\s(?P<line>\S*)\s(?P<addr>\S*):(?P<offset>[^:]*)')
trace_re = re.compile(r'(?P<pc>\S*):\s(?P<type>\S)\s(?P<addr>\S*)\s(?P<count>\S*)')

stall = 0
for line in input:
	match = trace_re.match(line)
	print(int(match.group('count')) + stall)
	for cache, delay in itertools.zip_longest(caches, opts.delays):
		stall += delay
		if cache and cache_re.match(cache.readline()).group('sym') == '@':
			continue
		break

