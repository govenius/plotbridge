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

# Tick formatting
#set format x "%.2g"

### Ticks ###

#set xtics 12.5,2,300 # for log scale
#set xtics 0,50,300 # for linear scale
#set xtics add ("200" 200)
#set mxtics 5


set format z "10^{\%L}"  # for 10^x format (for log scale)
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
# trace_35f49de81c3a4feb8dfa03cebd47c09f.bytes slowcoord = -0.9
# trace_aaa3a402024f42788ad13ecad91b0ef9.bytes slowcoord = -0.864
# trace_bf899a6538944631a1d843729814031a.bytes slowcoord = -0.828
# trace_a8faf7f638eb429183ab4ef38ab0cfc5.bytes slowcoord = -0.792
# trace_37241f93df8e4353acb7d042061ce9c4.bytes slowcoord = -0.756
# trace_05e23c24d1874fa3b4968daa98ec5500.bytes slowcoord = -0.72
# trace_4b9d16e40a8948a5834dca5ecf554d68.bytes slowcoord = -0.684
# trace_db8576b48a7745459c3115a8e9645740.bytes slowcoord = -0.648
# trace_93f0d46e4554483fb330c524b754644f.bytes slowcoord = -0.612
# trace_d9a7e12b42644cccbe65170db7c62a31.bytes slowcoord = -0.576
# trace_7fdab10a4f5f4c35a4f6190d6f375fb8.bytes slowcoord = -0.54
# trace_6427733302a848038e4a070e56fc660a.bytes slowcoord = -0.504
# trace_4387a396301b4edeae225df798ccb87d.bytes slowcoord = -0.468
# trace_379b42cba1f44c52b1778c54cf86b058.bytes slowcoord = -0.432
# trace_d0627df3d0c64cd8b801028019dc0297.bytes slowcoord = -0.396
# trace_c277f8f932de453e992ab8ec15b1bf01.bytes slowcoord = -0.36
# trace_a501111505d44e6b9fb6ef4e2a72103c.bytes slowcoord = -0.324
# trace_1347ffbc1cef49cc9f09107fa1a7ee3f.bytes slowcoord = -0.288
# trace_dada0ad4c8e3458b97241975ffe7c0df.bytes slowcoord = -0.252
# trace_13a5eeddac944a3ab8d2bcdca93bdba9.bytes slowcoord = -0.216
# trace_a904128dd5fa4f018d19ae9af9d8b2d4.bytes slowcoord = -0.18
# trace_88c878166ea346c3963035f282941bcf.bytes slowcoord = -0.144
# trace_760eca43877041ae9c29601e3666ba93.bytes slowcoord = -0.108
# trace_91580760b9344b4180faa3fde4f6a405.bytes slowcoord = -0.072
# trace_8f48be653f464950b3a05889e7f74c5b.bytes slowcoord = -0.036
# trace_57f86195e64446a8b9e7569fe997f0a9.bytes slowcoord = 0.0
# trace_412cc6122ba241919e5dacec4b250a56.bytes slowcoord = 0.036
# trace_960add2456a14884ae666b07a447e9b9.bytes slowcoord = 0.072
# trace_d4c99468890c4868bb04283aa3508603.bytes slowcoord = 0.108
# trace_105e2182c12345d3911f394c215ee8ad.bytes slowcoord = 0.144
# trace_7d30f983f00a4a5b9fcfd77715b156a0.bytes slowcoord = 0.18
# trace_b8e910e3a95b479686da5f502ec4988b.bytes slowcoord = 0.216
# trace_f4034904e80c4fabb9c45d33af50fae8.bytes slowcoord = 0.252
# trace_b094bedaec4b4624a2afd2a167d14cf5.bytes slowcoord = 0.288
# trace_8691340984ec46a7bb0fe529623970fd.bytes slowcoord = 0.324
# trace_319f77aa4bef4fed9584f1446dd2efbd.bytes slowcoord = 0.36
# trace_824923d16d174948811fb5eaabe0c40e.bytes slowcoord = 0.396
# trace_21128146963443ea824852430ea2e6a7.bytes slowcoord = 0.432
# trace_83a52ffbdf6948bc926d3f8ec47af87f.bytes slowcoord = 0.468
# trace_92254d50a4274403b90728902297ee32.bytes slowcoord = 0.504
# trace_157def84eaff43bd93ef49bd6abdeab3.bytes slowcoord = 0.54
# trace_b555598597a84686b5f0b539e84f5d3c.bytes slowcoord = 0.576
# trace_53ca24130f864a52a5cd786bab00c13f.bytes slowcoord = 0.612
# trace_e5eab2c7b4414983accfad460ae4673a.bytes slowcoord = 0.648
# trace_fb43429e8663435ebbe91748d8191a37.bytes slowcoord = 0.684
# trace_c6aa5f62bd8940b299fbda6113d45d42.bytes slowcoord = 0.72
# trace_0f1308317fa94e0289095ccebe9c974a.bytes slowcoord = 0.756
# trace_0f10745e089e4b3ab4950dc47861f986.bytes slowcoord = 0.792
# trace_5e9ccabcdba84e4bb56d2c0f6765ed60.bytes slowcoord = 0.828
# trace_285d0c9e521a4c4cb38e30f09a0d4086.bytes slowcoord = 0.864
# trace_9c5c6544f39d48208a658f83fca4dcfb.bytes slowcoord = 0.9




# Check if the qt terminal is available.
if (strstrt(GPVAL_TERMINALS, 'qt') > 0) interactive_terminal = "qt"; \
else interactive_terminal = "wxt enhanced"

set term @interactive_terminal size figwidth,figheight title "Transmission vs f and B" dashed
# replace "dashed" with "solid" if you want to ignore "linetype"/"lt" in plot

replot
bind Close "exit gnuplot"

