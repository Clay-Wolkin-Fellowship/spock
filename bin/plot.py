#!/bin/env python3
import os
import sys
import subprocess

gnuplot = '''
set key outside
set xlabel "Time to recache"
set ylabel "Number of replacements"
set title "%s"
set autoscale
set terminal png
set datafile separator ","
set output "%s"
plot %s
quit

'''

plot = '"%s" using 1:2 with lines title "%s"'
stddev = ', "%s" using 1:2:3 with yerrorbars title "STDEV"'

title  = sys.argv[1]
output = sys.argv[2]
inputs = sys.argv[3:]

plots = ", ".join(plot % (input, os.path.basename(input).split('.',2)[1]) for input in inputs)
if len(inputs) == 1:
	plots += stddev % inputs[0]
gnuplot = gnuplot % (title, output, plots)

proc = subprocess.Popen(["gnuplot","-persist"],stdin=subprocess.PIPE)
proc.communicate(gnuplot.encode('utf-8'))

