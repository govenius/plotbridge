#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np
np.random.seed(123) # makes automated testing easier

p = Plot(name='Histogram', template='gnuplot_2d_histogram',
         output_dir='.', overwrite=True)

p.set_xlabel('energy (keV)')
p.set_ylabel('count')

bin_edges = np.linspace(0,10,41)
bin_centers = bin_edges[:-1] + 0.5*np.diff(bin_edges)

for i in range(2): # add two (simulated) histograms
  counts = 100 * np.exp( -(bin_centers - (1+i)*3)**2 )
  counts += np.sqrt(counts)*np.abs(np.random.randn(len(counts)))
  p.add_trace(bin_centers, counts)

p.update()
p.run(interactive=True)
