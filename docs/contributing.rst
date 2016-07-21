Contributing
============

Contributions of all kinds are welcome, preferably through github.

Templates
---------

Template contributions are very welcome. Do try to keep in mind the
following:

* A new template should always be accompanied by at least one
  :doc:`example <examples>`.
* If you wish to modify an existing template, the modification should
  not (be likely to) break backwards compatibility.


Core code
---------

Some principles that should help keep the system simple and
maintainable in the long term:

* We provide a reasonable set of properties (xlabel, title, etc.)  for
  visualizing data, but fine tuning (e.g., details of tick marks) for
  "publication quality" plots is to be done directly in a custom
  template file.  It is a good idea to leave commented out examples of
  such fine tuning in the default templates.
* Options should be explicit, rather than \*args or \*kwargs, when
  possible.  We will also raise loud warnings (or exceptions) if we
  are not sure what the user wants.
* Trace data is stored in the binary :file:`trace_UUID.bytes` files
  only, i.e., no in-memory arrays should be stored after
  :meth:`plot.Plot.add_trace()` has returned.  This prevents errors
  originating from discrepancies in duplicate data and reduces the
  risk of memory leaks.
* The binary :file:`trace_UUID.bytes` files are the only method of
  transmitting the traces to plot engines. No ASCII files or pipes in
  Python. If necessary, write a separate :file:`.preprocess` script
  that does the necessary conversion before calling the actual plot
  engine.
* Only the trace data (not trace options) can be updated after
  :meth:`plot.Plot.add_trace()` has been called, just to keep things
  simple.  Updating the data is done by :meth:`plot.Plot.update_trace()`
  and it simply updates the corresponding binary
  :file:`trace_UUID.bytes` file.


Testing
-------

Currently plotbridge does not include proper unit tests. There is,
however, an automated way (:file:`test/test_examples.py`) to run all
the :doc:`examples <examples>` and compare the outputs to the expected
output (i.e. a previously generated version).
