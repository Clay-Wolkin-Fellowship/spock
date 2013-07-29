#!/bin/env python3
# Max Korbel
# Clay-Wolkin Fellowship
# rand replacement
# 2012 October 12

from optparse import OptionParser
import re
import subprocess
import sys
import random

# output file format
# \S*\s\S*\s\S*:[^:\s]*\s\S*
# action cache_addr  mem_addr : offset  mem_addr : offset
#                   |------NEW-------|  |-----VICTIM----|  <-- i just made victim tag


# parse command line options
parser = OptionParser()
parser.add_option("-o", "--offset", action="store", dest="offset", type=int,            help="bits of offset")
parser.add_option("-i", "--index" , action="store", dest="index" , type=int, default=0, help="bits of index" )
parser.add_option("-w", "--ways"  , action="store", dest="ways"  , type=int,            help="number of ways in the cache")

# 2^index = # of ways
# offset = # of offset bits
# sets = # of sets

# regular expression to extract instruction , type, and address from the trace
line_re = re.compile(r'0x(?P<instr>[0-9a-fA]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

#parse the arguments into options and args
(options, args) = parser.parse_args()

# the first argument is the trace file to read
input  = sys.stdin if args[0] == "-" else open(args[0],"r")

# the second argument is the output file
output = sys.stdout if args[1] == "-" else open(args[1],"w")


# the number of sets equals 2^(# of index bits)
num_sets = (1 << options.index)

num_ways = options.ways
num_words_per_line = (1 << options.offset)

# initialize cache as a list
cache = [None]*num_sets

removed = None

for line in input:

        #run the regex on this line
        parsed = line_re.match(line)
        if not parsed:
                continue

        # type of instruction (R or W)
        instr_type = parsed.group('type')
        
        # read in memory address (in base 16)
        mem_addr = int(parsed.group('addr'),16)

        # mask off the last options.offset bits to get the offset bits
        offset_bits = mem_addr & ((1 << options.offset) - 1)

        # the index is the set bits, shift away the offset and then grab the last options.index bits
        mem_index = (mem_addr >> options.offset) & ((1 << options.index) - 1)

        # the tag is the address minus without the byte offset and set index
        mem_tag = mem_addr >> (options.offset + options.index)

        # if the index does not exist yet in the cache, create it
        if cache[mem_index] is None:
                cache[mem_index] = []

        # if the address in this index exists already, keep it there
        if mem_tag in cache[mem_index]:
                # this symbol means the instruction is already in the cache
                sym = "@"
                
        elif len(cache[mem_index]) < num_ways:
                # this means that there is an open way in this set, put the data there
                sym = "<"
                cache[mem_index].append(mem_tag)
                
        else:
                # we must evict something, pick using random choice
                sym = "!"

                #pick a random number between [0, the number of ways)
                way_select = random.randint(0, num_ways-1)

                # save the old one to output what was removed
                removed = cache[mem_index][way_select]

                # put the new tag into the spot where the old one was removed from
                cache[mem_index][way_select] = mem_tag

        # print stuff to the output file
        output.write("%s . %x:%x:%x" % (sym, mem_tag, mem_index, offset_bits))
        if removed is not None:
                output.write(" %x:%x" % (removed, mem_index))
                removed = None
        output.write("\n");

                

input.close()
output.close()


