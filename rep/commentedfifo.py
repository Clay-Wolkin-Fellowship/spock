from optparse import OptionParser
import re
import sys
from collections import deque

parser = OptionParser()
parser.add_option("-o", "--offset", action="store", dest="offset", type=int,            help="bits of offset")
parser.add_option("-i", "--index" , action="store", dest="index" , type=int, default=0, help="bits of index" )
parser.add_option("-w", "--ways" , action="store", dest="ways" , type=int,            help="number of ways")
# Get instr = instruction, type = operation type, addr = operation target
line_re = re.compile(r'0x(?P<instr>[0-9a-f]*): (?P<type>[RW]) 0x(?P<addr>[0-9a-f]*)')

(options, args) = parser.parse_args()#what is the 'options'
input  = open(args[0],"r") #the input argument
output = open(args[1], "w")

num_sets = (1 << options.index) # Number of sets in cache = 2^index
num_ways = options.ways#set the number of ways (all taken from parser)
num_words_per_line = (1 << options.offset)
#can select the words per line!
cache = [None]*num_sets #make the cache
removed = None

for line in input:
	parsed = line_re.match(line)
	if not parsed:
		continue
	instr_type = parsed.group('type')
	mem_addr = int(parsed.group('addr'), 16)
	offset_bits = mem_addr & ((1 << options.offset) - 1) # Extract offset bits
	mem_index = (mem_addr >> options.offset) & ((1 << options.index) - 1)
	mem_tag = mem_addr >> (options.offset + options.index)

	if cache[mem_index] is None:
		cache[mem_index] = deque()#do we change the code here for 5%?	
	if mem_tag in cache[mem_index]:
		sym = "@"#recording as hit
	elif len(cache[mem_index]) < num_ways: # if there is a free way
		sym = "<"#cold miss/compulsory
		cache[mem_index].append(mem_tag)#adds entry
	else: # eviction time
		sym = "!"#capacity/conflict miss
		removed = cache[mem_index].popleft()
		cache[mem_index].append(mem_tag)

	# print output
	output.write("%s . %x:%x:%x" % (sym, mem_tag, mem_index, offset_bits))#hex
	if removed is not None:#write out the index and tag of what we evicted
		output.write(" %x:%x" % (removed, mem_index))
		removed = None
	output.write("\n");

                

input.close()
output.close()


