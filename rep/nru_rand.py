
#!/bin/env python3
# Max Korbel
# Clay-Wolkin Fellowship
# nru rand replacement
# 2012 October 26

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

# initialize cache as a list
cache = [None]*num_sets

# make a NRU list of 0's and 1's
nru_list = [None]*num_sets

# initialize the cache and recently used lists' ways
for i in range(0,num_sets):
        cache[i] = [None]*num_ways;
        nru_list[i] = [1]*num_ways;

# for NRU
# start off with all 1's (1 = not recently used)
# if you use it, make it a 0 (0 = recently used)
# if all are 0, make all 1

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
                        nru_list[mem_index][lnum] = 0
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
                                nru_list[mem_index][lnum] = 0
                                break
                        
                if emptyfound == 1:
                        sym = "<"


                ## This is where the replacement algorithm matters

                else:
                        # we must evict something
                        sym = "!"

                        # add the index of all lines in this set which are NRU
                        thiswaynru = []
                        for lnum in range(0, len(cache[mem_index])):
                                if nru_list[mem_index][lnum] == 1:
                                        thiswaynru.append(lnum)
                        
                        # set to all 1's if all are 0
                        if len(thiswaynru) == 0:
                                #print("All are recently used")
                                nru_list[mem_index] = [1]*num_ways
                                thiswaynru = []
                                for lnum in range(0, len(cache[mem_index])):
                                        if nru_list[mem_index][lnum] == 1:
                                                thiswaynru.append(lnum)

                        #pick a random number between [0, number of NRU)
                        way_select = random.randint(0, len(thiswaynru)-1)

                        # save the old one to output what was removed
                        removed = cache[mem_index][thiswaynru[way_select]]

                        # put the new tag into the spot where the old one was removed from
                        cache[mem_index][thiswaynru[way_select]] = mem_tag

                        # this one has now been recently used
                        nru_list[mem_index][way_select] = 0
                        
        # print stuff to the output file
        output.write("%s . %x:%x:%x" % (sym, mem_tag, mem_index, offset_bits))
        if removed is not None:
                output.write(" %x:%x" % (removed, mem_index))
                removed = None
        output.write("\n");

                

input.close()
output.close()


