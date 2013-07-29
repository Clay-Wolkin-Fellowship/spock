from optparse import OptionParser
import re
import sys
import random
from collections import deque

parser = OptionParser()
parser.add_option("-o", "--offset", action="store", dest="offset", type=int,            help="bits of offset")
parser.add_option("-i", "--index" , action="store", dest="index" , type=int, default=0, help="bits of index" )
parser.add_option("-w", "--ways" , action="store", dest="ways" , type=int,            help="number of ways")
# Get instr = instruction, type = operation type, addr = operation target
line_re = re.compile(r'0x(?P<instr>[0-9a-f]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

(options, args) = parser.parse_args()
input  = open(args[0],"r")
output = open(args[1], "w")

num_sets = (1 << options.index) # Number of sets in cache = 2^index
num_ways = options.ways#set the number of ways
num_words_per_line = (1 << options.offset)

cache = [None]*num_sets 
	# [least recently used -> most recently used]
removed = None
random.seed(3)#set the random seed for the generator
for line in input:
	choice=random.random()
	parsed = line_re.match(line)
	if not parsed:
		continue
	instr_type = parsed.group('type')
	mem_addr = int(parsed.group('addr'), 16) # Why are we converting to base 10?
	offset_bits = mem_addr & ((1 << options.offset) - 1) # Extract offset bits
	mem_index = (mem_addr >> options.offset) & ((1 << options.index) - 1)
	mem_tag = mem_addr >> (options.offset + options.index)

	if cache[mem_index] is None:
		cache[mem_index] = deque()#
	if mem_tag in cache[mem_index]:
		sym = "@" # Repetition
		cache[mem_index].remove(mem_tag)
		cache[mem_index].append(mem_tag) # Move mem_tag to end 
	elif len(cache[mem_index]) < num_ways: # if there is a free way
		sym = "<" # Pull
		cache[mem_index].append(mem_tag)
	else: # eviction time
		sym = "!" # Replacement
		removed = cache[mem_index].popleft() # Pop least recently used
		if choice<0.05:
			cache[mem_index].appendleft(mem_tag) # Pull new entry
		else:
			cache[mem_index].append(mem_tag)
	# print output
	output.write("%s . %x:%x:%x" % (sym, mem_tag, mem_index, offset_bits))
	if removed is not None:
		output.write(" %x:%x" % (removed, mem_index))
		removed = None
	output.write("\n");

                

input.close()
output.close()


