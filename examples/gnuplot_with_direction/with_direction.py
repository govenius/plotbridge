#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np

p = Plot('spiral', template='gnuplot_2d_with_direction',
         overwrite=True)
p.set_width(300); p.set_height(300)

t = np.linspace(0, 10*np.pi, 101)
curve_in_complex_plane = np.exp(-t/10. + 1j*t)

p.add_trace(curve_in_complex_plane)
p.update(); p.run()
