#!/usr/bin/python

import os
import numpy as np
import argparse
import logging
import re
import mmap

parser = argparse.ArgumentParser(description='Convert the binary trace data stored in .bytes files into text files.')

parser.add_argument("files",
                    nargs='+',
                    help="list of .bytes files you want to convert")

args = parser.parse_args()

for f in args.files:
  try:
    d = np.fromfile(f, dtype=np.float).reshape((-1,2))
  except:
    logging.exception("Failed to read %s", f)
    continue

  directory, f = os.path.split(os.path.abspath(f))

  # Try to extract the title from a gnuplot file.
  title = None
  xlabel = ''
  ylabel = ''
  try:
    for gnuplot_file in filter(lambda x: x.endswith('.gnuplot'), os.listdir(directory)):
      with open(os.path.join(directory, gnuplot_file), 'r+') as f_gp:
        m_gp = mmap.mmap(f_gp.fileno(), 0)

        m = re.search(r"set\s+xlabel\s\"(.*?)\"", m_gp, re.DOTALL)
        if m != None:
          #print m.group(0), m.groups()
          xlabel = m.group(1)
        m = re.search(r"set\s+ylabel\s\"(.*?)\"", m_gp, re.DOTALL)
        if m != None:
          #print m.group(0), m.groups()
          ylabel = m.group(1)

        m = re.search(f + r".+?\stitle\s\"(.*?)\"", m_gp, re.DOTALL)
        if m != None:
          #print m.group(0), m.groups()
          title = m.group(1)
          break
  except:
    logging.exception("Failed to find a corresponing title from a gnuplot file for %s", f)
    continue
  
  #print d.shape

  if title == None:
    f_out = (f[:-len('.bytes')] if f.endswith('.bytes') else f) + '.txt'
  else:
    def acceptable_char(x): return x.isalnum() or x in ['#', '-', '=']
    f_out = "".join(x if acceptable_char(x) else '_' for x in title) + '.txt'

  for k,v in {
      '{/Symbol W}': 'Ohm',
      '{/Symbol m}': 'u'
             }.iteritems():
    xlabel = xlabel.replace(k,v)
    ylabel = ylabel.replace(k,v)

  with open(f_out, 'w') as f_out:
    f_out.write(xlabel + "\t" + ylabel + "\n")
    np.savetxt(f_out, d, fmt='%.10e')
  logging.info("%s created.", f_out)


#dd.astype(np.float).tofile(trace_bytes + '.new')
