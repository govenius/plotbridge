#!/usr/bin/python

import os
import sys
import time
import logging
import subprocess

replot_poll_period = 1
plot_script_extension = '.gnuplot'

plot_script = None
for f in os.listdir('.'):
  if f.endswith(plot_script_extension):
    plot_script = f
    break
assert plot_script != None, 'No file ending with "%s" found in current directory.' % plot_script_extension

# Check if the plot script is already being plotted
# by another instance of the script
lock_file = plot_script + '.lock'

def refresh_lock():
  with open(lock_file, 'w') as lock:
    lock.write( "%.3f" % (time.time()) )

def exit_if_locked():
  try:
    with open(lock_file, 'r') as f:
      # the lockfile contains a timestamp
      if float(f.read()) > time.time() - max(3, 2*replot_poll_period):
        logging.warn("It seems that the file (%s) is already being plotted. Exiting...",
                     plot_script)
        exit()
  except IOError:
    return # lock doesn't exist

def print_plot_script(fname):
  with open(fname, 'r') as f:
    print('---start of %s---' % fname)
    for i,l in enumerate(f.read().split('\n')): print('%3d %s' % (i,l))
    print('---end of %s---\n' % fname)
    sys.stdout.flush()

exit_if_locked() # technically, this and the lock file creation should be done atomically...
try:
  refresh_lock()

  file_to_monitor = plot_script
  files_that_must_exist = [ plot_script ]

  plotted_once = False

  # Watch directory for changes and replot when necessary.
  # Use simple polling of st_mtime since it works on Linux and Windows
  # and the polling period is reasonably slow (~seconds).

  gp = None
  while not plotted_once or gp.poll() == None: # keep polling as long as gnuplot is alive

    if all( os.path.exists(ff) for ff in files_that_must_exist):
      if not plotted_once:

          # Initial plot
          plot_last_changed_time = os.path.getmtime(file_to_monitor)
          tex_last_changed_time = 0
          print_plot_script(plot_script)
          gp = subprocess.Popen(['gnuplot', plot_script, '-'], bufsize=0,
                                stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)
          plotted_once = True

          print("Replotting every %g seconds (if plot script modification time changes)..." % replot_poll_period)
          print("Hit <ctrl> + C to exit.")

      else:

        # Update plot if the plot script was modified
        try:
          plot_changed_time = os.path.getmtime(file_to_monitor)
          if plot_changed_time != plot_last_changed_time and gp != None:
            #logging.debug('Plot changed. Reloading plot script.')
            gp.stdin.write(('load "%s"\n' % plot_script).encode('utf-8'))
            plot_last_changed_time = plot_changed_time

          # compile .tex to PDF
          tex_to_watch = 'output.tex'
          if os.path.isfile(tex_to_watch):
            try:
              tex_changed_time = os.path.getmtime(tex_to_watch)
              if tex_changed_time != tex_last_changed_time:
                tex_last_changed_time = tex_changed_time
                with open('pdflatex.out', 'w') as log_file:
                  subprocess.call(['pdflatex', '-halt-on-error', 'output'], stdin=None, stdout=log_file, stderr=log_file)
            except:
              print('Call to pdflatex failed. See pdflatex.out.')

        except OSError:
          pass # the plot script does not exist which is normal if the plot was overwritten.

    time.sleep(replot_poll_period)
    refresh_lock()

finally:
  try: os.remove(lock_file)
  except: pass

  print("The plot engine has terminated. Exiting.")
