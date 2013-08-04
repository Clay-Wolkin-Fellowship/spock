#!/bin/env python3
from math import sqrt
from sys import stdin
def avgdev(xs):
	avg = sum(xs) / len(xs)
	var = sum((x - avg) ** 2 for x in xs)
	dev = sqrt(var / (len(xs) - 1) / len(xs))
	return (avg, dev)

xs = None
for line in stdin:
	if "total" in line: continue
	num, nxs = line.split(":")
	nxs = nxs.strip()
	nxs = [int(x) for x in nxs.split()]
	if not xs:
		xs = [0 for x in nxs]
	xs = [sum(x) for x in zip(xs,nxs)]
	if len(xs) == 1:
		print("%s,%d,0" % (num, xs[0]))
	else:
		avg,std = avgdev(xs)
		print("%s,%f,%f" % (num,avg,std))
if not xs:
	print("0,0,0")

	


