Installation
============

Get the latest version from `qithub <https://github.com/govenius/>`_
and run::

  python setup.py install --user

Requirements
------------

Besides the template-specific plot engine (e.g., `gnuplot
<http://www.gnuplot.info/>`_), you need:

  * `NumPy <http://www.numpy.org/>`_
  * `Jinja2 <http://jinja.pocoo.org/>`_ (>=2.7.2)


Ubuntu/Linux
^^^^^^^^^^^^
On Linux, numpy should be available in your package manager. In Ubuntu 16.04 for example::

  sudo apt-get install python-numpy python-jinja2

And for Gnuplot::

  sudo apt-get install gnuplot5-x11


Windows
^^^^^^^

On Windows, NumPy and Jinja2 are typically preinstalled in Python
distributions aimed at scientific computing, at least in `Python(x,y)
<http://python-xy.github.io/>`_.

A Windows installer for `gnuplot <http://www.gnuplot.info/>`_ is also
available.
