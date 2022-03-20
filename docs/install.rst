Installation
============

Get the latest version from `qithub
<https://github.com/govenius/plotbridge>`_, make sure you have the
:ref:`required packages <requirements>` installed, and run::

  pip install .

.. _requirements:

Requirements
------------

Besides the template-specific plot engine (e.g., `gnuplot
<http://www.gnuplot.info/>`_), you need:

  * `NumPy <http://www.numpy.org/>`_
  * `Jinja2 <http://jinja.pocoo.org/>`_ (>=2.7.2)
  * `Setuptools <https://setuptools.readthedocs.io/en/latest/>`_

You should probably be using a `Conda environment
<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_,
or some other way of managing the package dependencies.

If not, in Ubuntu 20.04 you can do::

  sudo apt-get install python3-numpy python3-jinja2 python3-setuptools

And for Gnuplot::

  sudo apt-get install gnuplot5-x11
