#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np
np.random.seed(123) # makes automated testing easier

p = Plot(name='Test IV', template='gnuplot_2d',
         output_dir='.', overwrite=True)
# You should now have a subdir "Test_IV" in your working dir.

# You can call p.run() immediately,
# the plot will be generated/updated whenever you
# call p.update().
p.run(interactive=True)

p.set_title('Fake IV')
p.set_fontsize(28)
p.set_xlabel('current (nA)'); p.set_xunits(1e-9)
p.set_ylabel('voltage (uV)'); p.set_yunits(1e-6)

current = np.linspace(-5e-9,5e-9,41)
p.set_xrange(-5.5, None) # None means autorange (in this
                         # case, only for the upper bound)

for i in range(2): # add two (simulated) measurements
  # Assume that the ideal response is linear (V = IR).
  voltage = (1 + i) * 3e3 * current

  # Simulate noise (correlated with the absolute voltage).
  errorbars = 0.1*np.abs(voltage)
  voltage += errorbars*np.random.randn(len(voltage))

  p.add_trace(current, voltage,
              yerr=errorbars,
              title='voltage %d' % i,
              lines=False, points=True,
              update=False) # update=True --> same as p.update()
  # each add_trace save the points in a binary file in "Test_IV".

p.update()
# This (re)generates Test_IV.gnuplot in "Test_IV".
#
# p.update() also executes gnuplot_2d.preprocess, although
# it's just an empty placeholder for the "gnuplot_2d" template.
