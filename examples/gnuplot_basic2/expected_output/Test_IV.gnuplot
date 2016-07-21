#!/usr/bin/gnuplot
#
# This file was generated from <TemplateReference 'gnuplot_header.template_fragment'>.
#

set macro

figwidth = 600
figheight = 300
dpi = 72. # This affects only the figure size and panel placement computations,
          # not the actual DPI values set in the output files
figwidth_in_inches = figwidth/dpi
figheight_in_inches = figheight/dpi

################################################################################################
# This multiplot layout code is adapted from http://www.sciencetronics.com/greenphotons/?p=570
# as an alternative to "set multiplot layout rows,cols".
# Original by Uwe Zimmermann, 2011 (CC BY-NC-SA 3.0).
mpl_top    = 0.4 #inch  outer top margin, title goes here
mpl_bot    = 0.5 #inch  outer bottom margin, x label goes here
mpl_left   = 1.0 #inch  outer left margin, y label goes here
mpl_right  = 0.02 #inch  outer right margin, y2 label goes here
mpl_dx     = 0.05 #inch  inter-plot horizontal spacing
mpl_dy     = 0.05 #inch  inter-plot vertical spacing
mpl_ny     = 2   #number of rows
mpl_nx     = 1   #number of columns

# calculate remaining free dimensions
mpl_width = ( figwidth_in_inches \
              - mpl_left - mpl_right \
              - (mpl_nx-1)*mpl_dx )/mpl_nx # width of individual plots
mpl_height = ( figheight_in_inches \
              - mpl_top - mpl_bot \
              - (mpl_ny-1)*mpl_dy )/mpl_ny # height of individual plots

# placement functions
#   rows are numbered from bottom to top
mpl_bot(n) = (mpl_bot+(n-1)*mpl_height+(n-1)*mpl_dy)/figheight_in_inches
mpl_top(n)  = 1-((mpl_top+(mpl_ny-n)*(mpl_height+mpl_dy))/figheight_in_inches)
#   columns are numbered from left to right
mpl_left(n) = (mpl_left+(n-1)*mpl_width+(n-1)*mpl_dx)/figwidth_in_inches
mpl_right(n)  = 1-((mpl_right+(mpl_nx-n)*(mpl_width+mpl_dx))/figwidth_in_inches)

mpl_set_panel(row, col) = sprintf("set lmargin at screen mpl_left(%d); \
                                   set rmargin at screen mpl_right(%d); \
                                   set tmargin at screen mpl_top(%d); \
                                   set bmargin at screen mpl_bot(%d)", \
                                   col, col, row, row)

# End of multiplot layout helper definitions.
# To set a panel, use "eval mpl_set_panel(row, column)"
################################################################################################

basefont = "Times,"

baselinewidth = 1.

unset multiplot

set terminal epslatex size figwidth_in_inches,figheight_in_inches color colortext standalone \
    font basefont linewidth baselinewidth \
    header "\\newcommand{\\ft}[0]{\\footnotesize}"
set output "output.tex"



set xlabel "current (nA)"
set ylabel "voltage ($\\mu$V)"
set y2label "$\\frac {dV}{dI}$ ($k\\Omega$)"

set grid


set title ""

###
# Some common formatting
###

# Tick formatting
#set format x "%.2g"

### Ticks ###

#set xtics 12.5,2,300 # for log scale
#set xtics 0,50,300 # for linear scale
#set xtics add ("200" 200)
#set mxtics 5



### For histograms ###
#set boxwidth 0.025
#set style fill transparent solid 0.5 noborder

### Annotation ###

# basic
#set label "label A"  at first  30, first  60   # in data coordinates

# more options
#set label "{/Arial-Bold label B}"  at graph  0.9, graph  0.72 \
#                                   rotate by 8 left \
#                                   tc rgb "#777777"

# legend position
#set key out vert # place legends outside the plot area
#set key cent right
#set key left top
#set key above title "Legend" box 3
set key outside

xunits = 1e-09
x2units = 1
yunits = 1e-06
y2units = 1000.0
zunits = 1

plot \
   "trace_fe199df08e7d4433957bf05a52083517.bytes" using (column(1)/xunits):(column(2)/yunits) every ::0:0 \
   binary format='%float64%float64' \
   with points \
     linecolor rgb "black" \
     pointtype 7 \
   title "voltage" \
     axes x1y1, \
        "trace_a7881b26dd664696b2104c76d29d8f3d.bytes" using (column(1)/xunits):(column(2)/y2units) every ::0:0 \
   binary format='%float64%float64' \
   with lines \
     linecolor rgb "red" \
     linetype 1 \
   title "$\\frac {dV}{dI}$" \
     axes x1y2  


# Check if the qt terminal is available.
if (strstrt(GPVAL_TERMINALS, 'qt') > 0) interactive_terminal = "qt"; \
else interactive_terminal = "wxt enhanced"

set term @interactive_terminal size figwidth,figheight  dashed
# replace "dashed" with "solid" if you want to ignore "linetype"/"lt" in plot

replot
bind Close "exit gnuplot"

