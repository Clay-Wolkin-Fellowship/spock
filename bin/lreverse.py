#!/bin/env python3
from sys import stdin
for line in stdin:
	print(line.rstrip('\n')[::-1])

