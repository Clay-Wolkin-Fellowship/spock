#!/bin/env python3
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
'''

plot = '"%s" using 1:2 with lines title "%s"'

title  = sys.argv[1]
output = sys.argv[2]
inputs = sys.argv[3:]

plots = ", ".join(plot % (input, os.path.basename(input).split('.',1)[0])
gnuplot = gnuplot % (title, output, inputs)

proc = subprocess.Popen(["gnuplot","-persist"],stdin=subprocess.PIPE)
proc.communicate(gnuplot)

