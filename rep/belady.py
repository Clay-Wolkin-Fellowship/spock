#!/bin/env python3
from collections import deque
from optparse import OptionParser
import re
import subprocess
import sys

# parse command line options
parser = OptionParser()
parser.add_option("-o", "--offset", action="store", dest="offset", type=int, default=3 ,  help="bits of offset")
parser.add_option("-i", "--index" , action="store", dest="index" , type=int, default=0 ,  help="bits of index" )
parser.add_option("-w", "--ways"  , action="store", dest="ways"  , type=int, default=16,  help="number of ways")


(options, args) = parser.parse_args()
try:
#	sl = subprocess.Popen("sl", shell=True)
	line_re = re.compile(r'0x(?P<instr>[0-9a-f]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

	ochars = len("%x" % ((1 << options.offset) - 1))
	ichars = len("%x" % ((1 << options.index ) - 1))
	lchars = len("%x" % (options.ways - 1))
	tchars = 0

	input  = open(args[0],"r")

	access = {}

	for i, line in enumerate(input):
#		if sl.poll() is not None:
#			sl = subprocess.Popen("sl", shell=True)
		parsed = line_re.match(line)
		if not parsed:
			continue
		type = parsed.group('type')

		oaddr = int(parsed.group('addr'),16)
		iaddr  = oaddr >> options.offset
		oaddr -= iaddr << options.offset
		addr   = iaddr >> options.index
		iaddr -= addr  << options.index

		tchars = max(tchars, len("%x" % addr))
		if iaddr not in access:
			access[iaddr] = {}
		if addr not in access[iaddr]:
			access[iaddr][addr] = deque()
		access[iaddr][addr].append(i)

	for iaddr in access.keys():
		for addr in access[iaddr].keys():
			access[iaddr][addr].append(i + 1)


	cache = {}
	input.close()
	input  = open(args[0],"r")
	output = open(args[1],"w")
	outline = "%%s 0x%%0%dx:%%0%dx 0x%%0%dx:%%0%dx:%%0%dx" % (ichars, lchars, tchars, ichars, ochars)
	victim  = " 0x%%0%dx:%%0%dx" % (tchars, ichars)

	for line in input:
#		if sl.poll() is not None:
#			sl = subprocess.Popen("sl", shell=True)
		parsed = line_re.match(line)
		if not parsed:
			continue
		type  = parsed.group('type')
		oaddr = int(parsed.group('addr'),16)

		iaddr  = oaddr >> options.offset
		oaddr -= iaddr << options.offset
		addr   = iaddr >> options.index
		iaddr -= addr  << options.index

		access[iaddr][addr].popleft()
		naddr = None
		if iaddr not in cache:
			cache[iaddr] = {}
		if addr in cache[iaddr]:
			sym = "@"
		elif len(cache[iaddr]) < options.ways:
			sym = "<"
			cache[iaddr][addr] = len(cache[iaddr])
		else:
			sym = "!"
			for caddr in cache[iaddr].keys():
				if naddr is None or access[iaddr][naddr][0] < access[iaddr][caddr][0]:
					naddr  = caddr
			cache[iaddr][addr] = cache[iaddr][naddr]
			del cache[iaddr][naddr]
		output.write(outline % (sym,iaddr,cache[iaddr][addr],addr,iaddr,oaddr))
		if naddr:
			output.write(victim % (naddr, iaddr))
		output.write("\n")
	input.close()
	output.close()
except:
	raise
#	sl.wait()
#	raise
# sl.wait()

