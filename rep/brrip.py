#!/bin/env python3
# Max Korbel
# Clay-Wolkin Fellowship
# BRRIP replacement
# 2013 March 4

# Run command example:
# python3 brrip.py ../traces/ls.mtrace ../results/ls.brrip -o 2 -i 8 -w 4 -m 2 -p 0.05

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
parser.add_option("-o", "--offset" , action="store", dest="offset" ,   type=int,            help="bits of offset")
parser.add_option("-i", "--index"  , action="store", dest="index"  ,   type=int, default=0, help="bits of index" )
parser.add_option("-w", "--ways"   , action="store", dest="ways"   ,   type=int,            help="number of ways in the cache")
parser.add_option("-m", "--agebits", action="store", dest="agebits",   type=int, default=2, help="M, the number of age bits for RRIP")
parser.add_option("-p", "--prob"   , action="store", dest="problong",  type=float, default=0.05, help="probability of using a long RRPV rather than a distant one")

# index is which set
# number of sets = 2^(# of index bits)
# number of ways (in each set)
# offset is for within a word, ignore for this...

# regular expression to extract instruction , type, and address from the trace
line_re = re.compile(r'0x(?P<instr>[0-9a-fA]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

#parse the arguments into options and args
(options, args) = parser.parse_args()

# the first argument is the trace file to read
input  = open(args[0],"r")

# the second argument is the output file
output = open(args[1],"w")


# the number of sets equals 2^(# of index bits)
num_sets = (1 << options.index)

num_ways = options.ways
num_words_per_line = (1 << options.offset)

# number of bits for RRIP age
M = options.agebits

# probability of using long RRPV instead of distant
p_long = options.problong

# starting ages (long and distant)
agestart_long = 2**M - 2
agestart_distant = 2**M - 1

# the oldest anything can be
maxage = 2**M - 1

# initialize cache as a list
cache = [None]*num_sets

# make a RRIP list of ages from 0 to 2^M - 1
rrip_list = [None]*num_sets

# initialize the cache and recently used lists' ways
for i in range(0,num_sets):
        cache[i] = [None]*num_ways;
        rrip_list[i] = [maxage]*num_ways;

# for NRU (M = 1)
# start off with all 1's (1 = not recently used)
# if you use it, make it a 0 (0 = recently used)
# if all are 0, make all 1

# for SRRIP (M > 1)
# cache hit:
#   (i)   set RRPV of block to '0'
# cache miss:
#   (i)   search for first '2^M - 1' from left
#   (ii)  if '2^M - 1' found go to step (v)
#   (iii) increment all RRPVs
#   (iv)  goto step (i)
#   (v)   replace block and set RRPV to 'agestart'

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


        ## Common sense for any cache:

        # if the address in this index exists already, keep it there
        samefound = 0
        for lnum in range(0, len(cache[mem_index])):
                if cache[mem_index][lnum] == mem_tag:
                        samefound = 1
                        rrip_list[mem_index][lnum] = 0
                        break
                
        if samefound == 1: 
                # this symbol means the instruction is already in the cache
                sym = "@"

        else:
                # put data into an empty one if possible
                emptyfound = 0
                for lnum in range(0, len(cache[mem_index])):
                        if cache[mem_index][lnum] is None:
                                cache[mem_index][lnum] = mem_tag
                                emptyfound = 1
                                rrip_list[mem_index][lnum] = 0
                                break
                        
                if emptyfound == 1:
                        sym = "<"


                ## This is where the replacement algorithm matters

                else:
                        # we must evict something
                        sym = "!"

                        
                        # age things until something is maximum age
                        thiswaynru = []
                        while len(thiswaynru) == 0:
                            # add the index of all lines in this set which are the maximum age
                            for lnum in range(0, len(cache[mem_index])):
                                    if rrip_list[mem_index][lnum] == maxage:
                                            thiswaynru.append(lnum)
                            
                            # increment all RRPV's if there are none with maximum age
                            if len(thiswaynru) == 0:
                                    #print("All are recently used")
                                    for lnum in range(0, len(cache[mem_index])):
                                        rrip_list[mem_index][lnum] += 1


                        #pick the first oldest age (from the left) as done in the paper
                        way_select = 0

                        # save the old one to output what was removed
                        removed = cache[mem_index][thiswaynru[way_select]]

                        # put the new tag into the spot where the old one was removed from
                        cache[mem_index][thiswaynru[way_select]] = mem_tag

                        # this one has now been added, make the age 'agestart' based on probability for BRRIP
                        if random.random() < p_long:
                            agestart = agestart_long
                        else:
                            agestart = agestart_distant
                        rrip_list[mem_index][way_select] = agestart
                        
                        
        # print stuff to the output file
        output.write("%s . %x:%x:%x" % (sym, mem_tag, mem_index, offset_bits))
        if removed is not None:
                output.write(" %x:%x" % (removed, mem_index))
                removed = None
        output.write("\n");

                

input.close()
output.close()


