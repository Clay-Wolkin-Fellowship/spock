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

counts = []
misses = []
access = {}
stage = "WARMUP"
snum = 0

line_re = re.compile(r'(?P<sym>\S*)\s(?P<line>\S*)\s(?P<addr>\S*):(?P<offset>[^:]*)(?:\s(?P<victim>\S*))')

with open(input,"r") as input:
	i = 0
	for line in input:
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
				counts[-1][ttr] = counts[-1].get(ttr,0) + 1
			elif stage == "SAMPLE":
				misses[-1] += 1
			if stage == "COOLDOWN":
				if victim in access:
					del access[victim]
			else:
				access[victim] = i
			i += 1
		if stage == "SAMPLE" and snum == opts.sample:
			snum = 0
			stage = "COOLDOWN"
		if stage == "COOLDOWN" and snum == opts.cooldown:
			snum = 0
			stage = "WARMUP"

sumcounts = ((i,[c.get(i,0) for c in counts]) for i in range(opts.cooldown) if any(i in c for c in counts))

with open(output,"w") as output:
	print("total: %s" % " ".join(str(m) for m in misses),file=output)
	for i,item in sumcounts:
		print("%d: %s" % (i, " ".join(str(it) for it in item)), file=output)


