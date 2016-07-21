#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np

p = Plot() # by default, Plot uses
           #   template='gnuplot_2d', (plot) name="plot",
           #   output_dir='.', and overwrite=False

x = np.linspace(0,10,201)
p.add_trace(x, np.sinc(x))

# Generate the output (i.e., the .gnuplot script
# stored in <output_dir>/<plot_name>).
p.update()

# Run the plot engine (gnuplot), i.e., execute the
# plot script generated in the subdir "plot".
# Since the template was 'gnuplot_2d', this will only
# work if you have gnuplot installed!
p.run()
