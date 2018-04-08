#!/usr/bin/gnuplot
#
# This file was generated from <TemplateReference 'gnuplot_header.template_fragment'>.
#

set macro

figwidth = 400
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
mpl_ny     = 1   #number of rows
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


pngdpi_per_screendpi = 96./72
figwidthinpng = ceil(figwidth*pngdpi_per_screendpi)
figheightinpng = ceil(figheight*pngdpi_per_screendpi)
set terminal pngcairo size figwidthinpng,figheightinpng enhanced \
    font basefont linewidth baselinewidth
set output "output.png"




set xlabel "frequency (GHz)"
set ylabel "B field (mT)"
set zlabel "S_{21}"

set logscale z
unset grid

set xrange [0.4:1.6]
set yrange [-0.8:0.8]
set zrange [0.001:1.05]

set title "Transmission vs f and B"

###
# Some common formatting
###

# In the classic color theme, linetype 5 is yellow which is hard to see on a white background.
set linetype 5 linecolor rgb "red"

# Tick formatting
#set format x "%.2g"

### Ticks ###

#set xtics 12.5,2,300 # for log scale
#set xtics 0,50,300 # for linear scale
#set xtics add ("200" 200)
#set mxtics 5
set mxtics
set mytics

logformat = "10^{\%L}"
set format z logformat  # for 10^x format (for log scale)
set ztics add ("1" 1)   # replace 10^0 by 1

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
set key right bottom

xunits = 1000000000.0
x2units = 1
yunits = 0.001
y2units = 1
zunits = 1

set cblabel "S_{21}"

set cbrange [0.001:1.05]

set logscale cb

set format cb "10^{\%L}"  # for 10^x format (for log scale)
#set cbtics add ("1" 1)   # replace 10^0 by 1


#set pm3d
set pm3d map # map projects the 3D surface onto the xy plane
set pm3d corners2color c1 # comment this out to take the mean of nearby points instead
#set pm3d interpolate 2,2
splot \
   "image_matrix.gnuplot_binary_matrix" \
   binary matrix \
   title ""

# This works well if you have evenly spaced "slow axis" data
#plot \
#   "image_matrix.gnuplot_binary_matrix" \
#   binary matrix with image \
#   title ""

## List of slow coordinate values (if any)
# trace_864dc67a61b84287a2e0ce3a9ae02c39.bytes slowcoord = -0.9
# trace_2ff62d2b638f4ef39d9a1c003231a8e2.bytes slowcoord = -0.864
# trace_516b6c91d8a24b76bc66d574c22e3504.bytes slowcoord = -0.828
# trace_6ab409361f5f4285b2d8b96a802d4fc3.bytes slowcoord = -0.792
# trace_5dd49d367d8a42b2be50f85efc544b6b.bytes slowcoord = -0.756
# trace_f1bfec386862488caa3f1399c1a01dd5.bytes slowcoord = -0.72
# trace_42c6aaaa961f40eca0bd50d1eb38d699.bytes slowcoord = -0.684
# trace_d1662072c9434a8ca3cad6b20668b6b7.bytes slowcoord = -0.648
# trace_05bfcbb5f92c4d2a9bab3b554e3e64b1.bytes slowcoord = -0.612
# trace_cd27969a8e25421b82ccba19756c9576.bytes slowcoord = -0.576
# trace_12096e85bee549e38f47d8ddffc1e394.bytes slowcoord = -0.54
# trace_7dc03c3c5aef4623a06dd778bb422bc3.bytes slowcoord = -0.504
# trace_c2516dd276b4408e8429c86a1634baf6.bytes slowcoord = -0.468
# trace_b37c6a8073d44da6a060087554b64604.bytes slowcoord = -0.432
# trace_be46a647b6de4ca983b330c53cae3555.bytes slowcoord = -0.396
# trace_b71a1962260e4166b0fefd5304d66e9c.bytes slowcoord = -0.36
# trace_4ede7feaaa64498e967d60618af23b9d.bytes slowcoord = -0.324
# trace_feca314264b54e159f772fe2076ea681.bytes slowcoord = -0.288
# trace_4fe9551e90e044ecb458a32a2fd7e92e.bytes slowcoord = -0.252
# trace_be63878286634c4397c14e7c4202c091.bytes slowcoord = -0.216
# trace_927e7cdbfcb848baa87efaf1ddcf8052.bytes slowcoord = -0.18
# trace_2641622f899042ac87405335f43e0ae9.bytes slowcoord = -0.144
# trace_9db956dcc9754ba298d4a1e713a35e93.bytes slowcoord = -0.108
# trace_9752cab43c7b48ffbe20df2145932679.bytes slowcoord = -0.072
# trace_7d65f7b0e8694cb68c1cdb9dab115ff1.bytes slowcoord = -0.036
# trace_57561935f6234d2683c3e7e8990fa3a2.bytes slowcoord = 0.0
# trace_3bf8bce808f6404dae395b2e3da3dcf5.bytes slowcoord = 0.036
# trace_82f8c04a63c7451bb9d17198c03a6fa6.bytes slowcoord = 0.072
# trace_93f92332a51d437785490c4f6340da9f.bytes slowcoord = 0.108
# trace_4a464b0bfe384fbcb96edff867fdf3a9.bytes slowcoord = 0.144
# trace_5902731819654caea1db8a394347cc0d.bytes slowcoord = 0.18
# trace_c6f2d4a9141d44d386499731f3d3a0b2.bytes slowcoord = 0.216
# trace_ad0e6767542a4ec6a734defa68ec82a5.bytes slowcoord = 0.252
# trace_9e3aa2f92c9e4889ba244e15f958f5ea.bytes slowcoord = 0.288
# trace_588ff4d3d3de487a96935e767f3b1ed9.bytes slowcoord = 0.324
# trace_0e8e1ecb36ae4d61850b418c1d9562e3.bytes slowcoord = 0.36
# trace_2cad5ba4d343458382a0959cf801a6cd.bytes slowcoord = 0.396
# trace_f21028150dea4fa7b05d61f9246f6a02.bytes slowcoord = 0.432
# trace_112e4c666d8b4837aea77030fd0badc7.bytes slowcoord = 0.468
# trace_4adc19db82514407a4bbf4665adaf160.bytes slowcoord = 0.504
# trace_c204f0c4a0504d28970f398e7b540b8a.bytes slowcoord = 0.54
# trace_7c86adea703649de819a6f6a5351d07f.bytes slowcoord = 0.576
# trace_2f5e2c8538f449b4ad56c51ef4ca2d7b.bytes slowcoord = 0.612
# trace_3a40c7375bbf445f8a1dfe102ebd4474.bytes slowcoord = 0.648
# trace_0308c05612cb4bfca43e77e448b8e12b.bytes slowcoord = 0.684
# trace_69b8397f243a4ffcacc7b2dff0a9a61e.bytes slowcoord = 0.72
# trace_e5d0b58c1d4a4b9cb7580266004f53f6.bytes slowcoord = 0.756
# trace_b22b71c5237d4b8793c97f63bcd215bc.bytes slowcoord = 0.792
# trace_8d8eface89684053bc23ffd27294e075.bytes slowcoord = 0.828
# trace_5558b530580f4026b2b787e14690f033.bytes slowcoord = 0.864
# trace_511c363b698b4cd9a00641364012f9b0.bytes slowcoord = 0.9




# Check if the qt terminal is available.
if (strstrt(GPVAL_TERMINALS, 'qt') > 0) interactive_terminal = "qt"; \
else interactive_terminal = "wxt enhanced"

set term @interactive_terminal size figwidth,figheight title "Transmission vs f and B" dashed
# replace "dashed" with "solid" if you want to ignore "linetype"/"lt" in plot

replot
bind Close "exit gnuplot"

