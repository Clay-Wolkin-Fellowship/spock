#!/bin/env python3
from math import sqrt
from sys import stdin, argv

bucketsize = int(argv[1])
current = bucketsize
def avgdev(xs):
	avg = sum(xs) / len(xs)
	var = sum((x - avg) ** 2 for x in xs)
	dev = sqrt(var / (len(xs) - 1) / len(xs))
	return (avg, dev)

xs = None
for line in stdin:
	if "total" in line: continue
	num, nxs = line.split(":")
	num = int(num)
	nxs = [int(x) for x in nxs.strip().split()]
	if not xs:
		xs = [0 for x in nxs]
	while current < num:
		center = current - bucketsize / 2
		if len(xs) == 1:
			print("%d,%d,0" % (center, xs[0]))
		else:
			avg,std = avgdev(xs)
			print("%d,%f,%f" % (center,avg,std))
		current += ((num - current) // bucketsize + 1) * bucketsize
		xs = [0 for x in xs]
	xs = [sum(x) for x in zip(xs,nxs)]

center = current - bucketsize / 2
if not xs:
	print("0,0,0")
elif len(xs) == 1:
	print("%d,%d,0" % (center, xs[0]))
else:
	avg,std = avgdev(xs)
	print("%d,%f,%f" % (center,avg,std))

	

	


