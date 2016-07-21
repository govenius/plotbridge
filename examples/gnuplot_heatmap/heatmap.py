#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np
np.random.seed(123) # makes automated testing easier

p = Plot('Transmission vs f and B',
         template='gnuplot_2d_stacked_image',
         overwrite=True)

p.set_width(400)
p.set_height(300)
p.set_xlabel('frequency (GHz)'); p.set_xunits(1e9)
p.set_ylabel('B field (mT)'); p.set_yunits(1e-3)
p.set_zlabel('S_{21}')
p.set_zlog(True)
p.set_grid(False)

for bfield in np.linspace(-.9e-3, .9e-3, 51):
  f0 = 1.3e9 - 1e9*np.abs(bfield/1e-3)**2
  w = 30e6
  freq = np.linspace(f0 - 400e6, f0 + 400e6, 101) # Hz
  transmission = 1 / ( 1 + (2*(freq-f0)/w)**2 ) # fake data
  transmission += np.abs( 0.02 * np.random.randn(len(transmission)) ) # fake noise
  p.add_trace(freq, transmission,
              slowcoordinate=bfield)

p.set_xrange(0.4, 1.6) # None, None --> autorange
p.set_yrange(-.8, .8)
p.set_zrange(1e-3, 1.05)

p.update()
p.run()
