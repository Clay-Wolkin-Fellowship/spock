#!/bin/sh
cat gplot/single.gplot | sed "s|INPUT|$1|" | sed "s|OUTPUT|$2|" | gnuplot -persist
