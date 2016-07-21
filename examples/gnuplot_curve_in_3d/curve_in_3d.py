#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np

p = Plot('spirals', template='gnuplot_3d',
         overwrite=True)
p.set_width(600); p.set_height(600)
p.set_xlabel('x(t)')
p.set_ylabel('y(t)')
p.set_zlabel('t')

t = np.linspace(0, 10*np.pi, 101)
curve_in_complex_plane = np.exp(-t/10. + 1j*t)

# This interprets the real and imag parts
# as the x and y coordinates
p.add_trace(t, curve_in_complex_plane,
            lines=True)

# You can also specify the components as a matrix
curve_in_complex_plane *= np.exp(1j*np.pi)
p.add_trace([ curve_in_complex_plane.real,
              curve_in_complex_plane.imag,
              t],
            lines=True)

p.update(); p.run()
