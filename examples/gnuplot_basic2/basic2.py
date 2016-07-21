#!/usr/bin/python

from plotbridge.plot import Plot
import numpy as np
np.random.seed(123) # makes automated testing easier

p = Plot(name='Test IV', template='gnuplot_2d',
         output_dir='.', overwrite=True)
p.run(interactive=True)

# Export a PDF, this is implemented with epslatex in the template, so
# use LaTex format for all strings.
#
# Note: the on-screen interactive version (wxt) does not support
# LaTeX, but the correctly rendered version will show up in
# Test_IV/output.pdf.
p.set_export_format('pdf')

p.set_title('')
p.set_width(600)
p.set_height(300)

p.set_xlabel(r'current (nA)'); p.set_xunits(1e-9)
p.set_ylabel(r'voltage ($\\mu$V)'); p.set_yunits(1e-6)
p.set_y2label(r'$\\frac {dV}{dI}$ ($k\\Omega$)'); p.set_y2units(1e3)

current = np.linspace(-5e-9, 5e-9, 81)
voltage = 3e3 * 1e-9*np.tanh(current/1e-9) # simulate ideal response
voltage += 0.02e-6*np.random.randn(len(voltage)) # simulate noise

p.add_trace(current, voltage,
            title='voltage',
            color='black',
            lines=False, points=True)

p.add_trace(current[:-1] + 0.5*np.diff(current),
            np.diff(voltage)/np.diff(current),
            title=r'$\\frac {dV}{dI}$',
            color='red',
            lines=True, points=False,
            right=True) # plot this trace on the y2 axis

# Pass plot-specific other options.
# In this case, the legend placement directive.
p.set_other_options({'key': 'outside'})

p.update()
