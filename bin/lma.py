#!/bin/env python3

import re
import subprocess
import sys
import random

# parse command line options
parser = OptionParser()
parser.add_option("-o", "--offset", action="store", dest="offset", type=int, help="bits of offset")

# regular expression to extract instruction , type, and address from the trace
line_re = re.compile(r'0x(?P<instr>[0-9a-fA]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

#parse the arguments into options and args
(options, args) = parser.parse_args()

# the first argument is the trace file to read
input  = sys.stdin if args[0] == "-" else open(args[0],"r")

# the second argument is the output file
output = sys.stdout if args[1] == "-" else open(args[1],"w")

seen = {}

for i,line in enumerate(input):
        #run the regex on this line
        parsed = line_re.match(line)
        if not parsed:
                continue

        mem_addr = int(parsed.group('addr'),16)
	cache_addr = mem_addr >> options.offset
	print(seen.get(cache_addr,-1),file=output)
	seen[cache_addr] = i
                
input.close()
output.close()


