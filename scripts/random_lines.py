#!/bin/env python3
from collections import deque
from itertools import chain
from random import randrange
from sys import stdin

def group(i, k):
	g = deque(maxlen=k)
	for item in i:
		g.append(item)
		if len(g) == k:
			yield "".join(g)

def select(i, n):
	s = []
	for item in i:
		if len(s) < n:
			s.append(item)
		else:
			j = randrange(len(s)+1)
			if j < len(s):
				s[j] = item
	return s
try:
	from argparse import ArgumentParser
	parser = ArgumentParser(description='Selects N runs of length K from a file')
	parser.add_arguments('n', metavar='N', type=int, help='Number of runs')
	parser.add_arguments('k', metavar='K', type=int, default=1, help='Length of runs')
	parser.add_arguments('input', metavar='FILE', type=open, default=stdin, help='Input file')
except ImportError:
	class Args(object):
		def __init__(self, args):
			self.n = int(args[0])
			self.k = int(args[1]) if len(args) > 1 else 1
			self.input = open(args[2], 'r') if len(args) > 2 else stdin
	from sys import argv, exit
	if len(argv) == 1:
		print("usage: %s N [K] [FILE]" % argv[0])
		exit(1)
	parser = Args(argv[1:])

print("".join(select(group(parser.input, parser.k), parser.n)),end='')

