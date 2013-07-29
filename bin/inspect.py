#!/bin/env python3
from string import printable

lookup = {}
for i in range(256):
	if chr(i) in printable:
		lookup[i] = chr(i)
lookup[ord('\\')] = r'\\'
lookup[ord('\n')] = r'\n'
lookup[ord('\'')] = r"\'"
lookup[ord('\a')] = r'\a'
lookup[ord('\b')] = r'\b'
lookup[ord('\f')] = r'\f'
lookup[ord('\n')] = r'\n'
lookup[ord('\r')] = r'\r'
lookup[ord('\t')] = r'\t'
lookup[ord('\v')] = r'\v'
lookup[ord('\0')] = r'\0'

import sys
def write(f):
	try:
		byte = f.read(1)
		while byte:
			byte = ord(byte)
			if byte in lookup:
				print("0x%02x %03d '%s'" % (byte, byte, lookup[byte]))
			else:
				print("0x%02x %03d" % (byte, byte))
			byte = f.read(1)
	except IOError:
		pass

if len(sys.argv) > 1:
	with open(sys.argv[1], 'rb') as f:
		write(f)
else:
	write(sys.stdin)

