#!/bin/env python3
import optparse
import re
import sys

parser = optparse.OptionParser()
parser.add_option("-w","--warmup",dest="warmup",type=int)
parser.add_option("-s","--sample",dest="sample",type=int)
parser.add_option("-c","--cooldown",dest="cooldown",type=int)

(opts, args) = parser.parse_args()

input  = args[0]
output = args[1]
wtime  = args[2]

counts = []
misses = []
access = {}
stage = "WARMUP"
snum = 0
mwttr = 0

line_re = re.compile(r'(?P<sym>\S*)\s(?P<line>\S*)\s(?P<addr>\S*):(?P<offset>[^:]*)(?:\s(?P<victim>\S*))')

with open(input,"r") as input:
	for i, line in zip(open(wtime), input):
		i = int(i.strip())
		match = line_re.match(line)
		if not line:
			print("error line %d" % i)
			continue
		snum += 1
		if stage == "WARMUP":
			if snum == opts.warmup:
				counts.append({})
				misses.append(0)
				access = {}
				snum = 0
				stage = "SAMPLE"
			continue
		addr   = match.group('addr')
		victim = match.group('victim')
		if victim:
			if addr in access:
				ttr = i - access[addr]
				mwttr = max(mwttr, ttr)
				counts[-1][ttr] = counts[-1].get(ttr,0) + 1
			elif stage == "SAMPLE":
				misses[-1] += 1
			if stage == "COOLDOWN":
				if victim in access:
					del access[victim]
			else:
				access[victim] = i
		if stage == "SAMPLE" and snum == opts.sample:
			snum = 0
			stage = "COOLDOWN"
		if stage == "COOLDOWN" and snum == opts.cooldown:
			snum = 0
			stage = "WARMUP"

sumcounts = ((i,[c.get(i,0) for c in counts]) for i in sorted(set(i for c in counts for i in c.keys())))

with open(output,"w") as output:
	print("total: %s" % " ".join(str(m) for m in misses),file=output)
	for i,item in sumcounts:
		print("%d: %s" % (i, " ".join(str(it) for it in item)), file=output)


