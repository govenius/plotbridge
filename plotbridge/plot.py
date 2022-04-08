from plotbridge._metadata import __version__

import logging
import os
import stat
import shutil
import time
import types
import numpy as np
import uuid
from collections import OrderedDict
import itertools
import subprocess
import re

 # Python 2/3 compatibility
try:
  basestring # Python 2
except NameError:
  basestring = str # Python 3

try:
  import configparser # Python 3
except ModuleNotFoundError:
  import ConfigParser as configparser # Python 2


class Plot():
  '''Container for a set of traces ("a plot") and a
  template based system for generating a script that plots them.

  Takes in **global** (i.e. per-plot) **options**
  together with a set of traces (data + **per-trace options**).

  The inputs to plotbridge are (a) the data points and basic plot
  options from Python and (b) a template from a text file.
  Optionally, you can include a *preprocess* script (e.g. in Python)
  that massages the data before passing it to your plotting program.
  '''

  _already_warned_about_subprocess_version = False

  def __init__(self, name=None, template='gnuplot_2d', output_dir=None, overwrite=False):
    '''
    Create a plot object.

    :param name: default will be 'plot<n>'
    :param template: the template (e.g. 'gnuplot_2d') for generating the output,
                     see the default_templates subdir for available built-in alternatives
                     or provide a path to your own custom template.
    :param output_dir: where output subdir <name> should be created,
                       default is current working dir.
    :param overwrite: If False, append a number to output_dir if it already exists.
    '''

    parent_dir = (output_dir if output_dir != None else '.')
    assert os.path.isdir(parent_dir), '%s is not a directory.' % parent_dir

    self._set_name(name, parent_dir, not overwrite)

    # this should give us <installation_dir>/plotbridge/default_templates
    self._default_template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'default_templates')
    self._template_frags_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'template_fragments')
    self._common_helper_scripts_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'common_helper_scripts')

    self._template_frags_cache = {}
    self._set_template(template)

    # dict of per-trace-properties, keys are trace_ids (i.e. random UUIDs)
    self._traces = OrderedDict()

    # per-plot-properties
    self._global_opts = {}
    self.reset_options()

    # create the output directory and copy the helper files there
    self.update()

  ##############
  #
  # Plot wide operations
  #
  ##############  

  def _set_name(self, name, parent_dir, auto_increment):
    '''Internal: Set the plot name. (call only from __init)'''

    if name == None: name = 'plot'
    self._name = name 

    path_friendly_name = self.get_name(path_friendly=True)
    assert len(path_friendly_name) > 0, 'invalid name %s' % name
    d = os.path.join(parent_dir, path_friendly_name)

    if auto_increment:
      # Append a number to name if the dir already exists
      i = 2
      while os.path.isdir(d):
        self._name = '%s %d' % (name, i)
        d = os.path.join(parent_dir, '%s_%d' % (path_friendly_name, i))
        i += 1

    if os.path.exists(d):

      self._output_dir = d
      logging.info('Removing contents of old "%s"', d)
      try:
        for f in os.listdir(d):
          if f.endswith('.lock'): continue # don't remove lock files
          ppp = os.path.join(d,f)
          try:
            if   os.path.isfile(ppp) or os.path.islink(ppp): os.unlink(ppp)
            elif os.path.isdir(ppp): logging.warn('Ignoring directory %s', ppp) #shutil.rmtree(ppp)  # Normally there are no subdirs, so stay on the safe side and don't delete them...
          except:
            pass # files may be locked by other processes (especially on Windows), keep removing others
      except:
        logging.exception('Could not remove old %s', d)

    else:

      try:
        # Don't create parent dirs automatically (os.makedirs), because it's likely
        # that there's a typo in the path if parent_dir does not exist.
        os.mkdir(d)
        self._output_dir = d
      except:
        logging.exception('Could not create %s. Are you sure the parent exists and is writable by you?', d)
        raise

  def get_name(self, path_friendly=False):
    '''Get the plot name.

    :param path_friendly: replace potentially problematic characters by "_"
    '''
    if not path_friendly:
      return self._name
    else:
      def acceptable_char(x): return x.isalnum() or x in ['#', '-', '=']
      # leave out non-alphanumeric characters
      return "".join(x if acceptable_char(x) else '_' for x in self._name)

  def get_output_dir(self):
    '''Get output dir name.'''
    return os.path.abspath(self._output_dir)

  def _set_template(self, template):
    '''
    Internal: Set the template name. (call only from __init)
    '''
    template_name = os.path.split(template.strip('/\\'))[1]
    abspath = os.path.abspath(os.path.join(template, template_name + '.template'))
    try: # see if a full path was already given
      with open(abspath, 'r') as f:
        f.read(1) # see if we can read the .template file
      self._template = abspath
      return
    except: # otherwise, look in the default templates dir
      try:
        absdefpath = os.path.join(self._default_template_path, template_name, template_name + '.template')
        
        with open(absdefpath, 'r') as f: f.read(1) # see if we can read the .template file
        self._template = absdefpath
        return
      except:
        logging.exception('Could not find (or read) a template in %s or %s.', abspath, absdefpath)
        raise

  def _get_template_fragment(self, frag):
    '''Return the specified template fragment.

    Note: this caches the fragments, which means that they will NOT be
    reloaded, if changed. Rhat should be OK since you generally
    shouldn't change them anyway.
    '''
    if not frag in self._template_frags_cache.keys():
      try:
        with open(os.path.join(self._template_frags_path, frag + '.template_fragment'), 'r') as f:
          self._template_frags_cache[frag] = f.read()
      except:
        logging.warn('Could not load a template fragment called %s from %s.',
                     frag, self._template_frags_path)
        raise

    return self._template_frags_cache[frag]

  def get_template(self):
    '''returns the full path to the .template file used for this plot as
    a triple (directory, filname, extension).
    '''
    template_dir, template_file = os.path.split(self._template)
    ext_start = template_file.rindex('.')
    return template_dir, template_file[:ext_start], template_file[ext_start+1:]

  def clear(self, update=False):
    '''Remove all traces.

    :param update: update plot script?
    '''
    logging.info('Clearing plot %s...', self._name)
    for trace_id in list(self._traces.keys()): self.remove_trace(trace_id, update=False)
    if update: self.update()

  def update(self):
    '''Regenerate the outputs based on the specified template.'''
    from jinja2 import Environment, FileSystemLoader

    template_dir, template_name, template_ext = self.get_template()
    template_file = template_name + '.' + template_ext

    env = Environment( loader=FileSystemLoader([ template_dir, self._template_frags_path]),
              trim_blocks=True,
              keep_trailing_newline=True) # This option requires at least version 2.7 of jinja2

    def defaultget(arr, key, default=''):
      try: return arr[key]
      except KeyError: return default

    env.filters['defaultget'] = defaultget
    env.filters['isint'] = lambda x: isinstance(x, int)
    env.filters['ifnone'] = lambda x, default='': default if x == None else x
    env.filters['allnone'] = lambda x: min(map(lambda y: y == None, x)) # check if all entries of iterable are None

    try:
      template = env.get_template(template_file)
    except:
      logging.warn('Could not parse the template from %s. '
                   'Refer to the Jinja2 documentation for valid syntax.',
                   self.get_template())
      raise

    cfg = self._read_config()

    trace_opts = []
    for trace_id in self._traces.keys():
      d = dict(self._traces[trace_id])
      d['bytesfile'] = 'trace_%s.bytes' % trace_id
      trace_opts.append(d)

    # Generate the plot script
    # Write to a temp file (.new) first and rename it once its complete.
    # This way the update is atomic from the point of view of
    # external programs that monitor changes to the file.
    out_dir = self.get_output_dir()
    plot_script = os.path.join(out_dir, self.get_name(path_friendly=True) + cfg['extension'])
    with open(plot_script + '.new', 'w') as f:
      f.write( template.render(global_opts=self._global_opts, traces=trace_opts) )
    shutil.move(plot_script + '.new', plot_script)

    if os.name != 'nt' and ('executable' in cfg.keys()) and bool(cfg['executable']):
      # Make the plot script executable
      st = os.stat(plot_script)
      os.chmod(plot_script, st.st_mode | stat.S_IXUSR | stat.S_IXGRP)

    # Copy the interactive script, if any
    if 'interactive-script' in cfg.keys() and len(cfg['interactive-script'].strip()) > 0:
      interactive_script_src_path, self._interactive_script = self._get_helper_file_path(cfg['interactive-script'])
      shutil.copy(interactive_script_src_path, os.path.join(out_dir, self._interactive_script))

    # Copy other helper files associated with the template (i.e. all other
    # files in the directory that don't look like temp files.)
    for helper_file in os.listdir(template_dir):
      if (helper_file.endswith('~')
        or helper_file.startswith('.')
        or helper_file.startswith('#')
        or helper_file.startswith('_')
        or helper_file.endswith('.template')
        or helper_file.endswith('.cfg')): continue
      shutil.copy(os.path.join(template_dir, helper_file),
                  os.path.join(out_dir, helper_file))


    if 'preprocess-script' in cfg.keys() and len(cfg['preprocess-script'].strip()) > 0:
      # Copy the preprocess script, if any
      preprocess_script_src_path, preprocess_script = self._get_helper_file_path(cfg['preprocess-script'])
      preprocess_script = os.path.abspath( os.path.join(out_dir, preprocess_script) )
      shutil.copy(preprocess_script_src_path, preprocess_script)

      interpreter = cfg['preprocess-interpreter'] if 'preprocess-interpreter' in cfg.keys() else ''
      try:

        try:
          # This back-ported version includes the "timeout" parameter
          from subprocess32 import call
        except:
          # Otherwise, use the standard module, which only includes "timeout" for Python >= 3.3
          from subprocess import call


        log_file = preprocess_script + '.out'

        preprocess_timeout = max(1, int(cfg['preprocess-timeout'])) if 'preprocess-timeout' in cfg.keys() else 15.
        if len(interpreter) > 0: call_args = [ interpreter, preprocess_script ]
        else:                    call_args = [ preprocess_script ]
        logging.info('Executing %s. Output in %s.' % (preprocess_script, log_file))
        with open(log_file, 'w') as log_file:
          try:
            call(call_args, cwd=out_dir, stdin=None, stdout=log_file, stderr=log_file,
                 timeout=preprocess_timeout)
          except:
            preprocess_start_time = time.time()
            subprocess.call(call_args, cwd=out_dir, stdin=None, stdout=log_file, stderr=log_file)
            if not Plot._already_warned_about_subprocess_version and (
                time.time()-preprocess_start_time > preprocess_timeout/4.):
              logging.warn('The preprocess script %s worked but took a while. Your version of subprocess.call() does not support the timeout parameter so the preprocess script can block execution indefinitely (if it hangs). You are encouraged to install the back-ported subprocess32 module ("pip install subprocess32").', preprocess_script)
              Plot._already_warned_about_subprocess_version = True

      except:
        logging.exception('Failed to execute %s', preprocess_script)



  def run(self, interactive=True):
    '''
    Execute the generated plot script.

    :param interactive: If true, execute the .interactive script instead.
    '''

    cfg = self._read_config()
    template_dir, template_name, template_ext = self.get_template()
    out_dir = os.path.abspath(self.get_output_dir())

    if interactive:
      plot_script = self._interactive_script
      interpreter = cfg['interactive-interpreter'] if 'interactive-interpreter' in cfg.keys() else ''
    else:
      plot_script = self.get_name(path_friendly=True) + cfg['extension']
      interpreter = cfg['interpreter'] if 'interpreter' in cfg.keys() else ''

    p_args = ( [ interpreter, os.path.join(out_dir, plot_script) ]
               if len(interpreter) > 0 else
               [ os.path.join(out_dir, plot_script) ] )

    log_file = os.path.join(out_dir, '%s.out' % (plot_script))
    i = 2 # Append a number to the log file if it already exists
    while os.path.exists(log_file):
      log_file = os.path.join(out_dir, '%s.out%d' % (plot_script, i))
      i += 1

    logging.info('Executing %s. Log messages in %s.', plot_script, log_file)

    with open(log_file, 'a') as log_file:
      subprocess.Popen(p_args, cwd=out_dir,
                       stdin=None, stdout=log_file, stderr=log_file)


  ##############
  #
  # Global plot properties
  #
  ##############

  def reset_options(self):
    ''' Set global plot properties back to defaults. '''
    export_formats = self.get_export_formats()
    self.set_xunits()
    self.set_x2units()
    self.set_yunits()
    self.set_y2units()
    self.set_zunits()
    self.set_export_format(export_formats[0] if len(export_formats)>0 else None)
    self.set_show_on_screen()
    self.set_width()
    self.set_height()
    self.set_fontsize()
    self.set_title(self.get_name())
    self.set_legend()
    self.set_xlabel()
    self.set_x2label()
    self.set_ylabel()
    self.set_y2label()
    self.set_zlabel()
    self.set_cblabel()
    self.set_xlog()
    self.set_x2log()
    self.set_ylog()
    self.set_y2log()
    self.set_zlog()
    self.set_xrange()
    self.set_x2range()
    self.set_yrange()
    self.set_y2range()
    self.set_zrange()
    self.set_grid()
    self.set_other_options()

  def set_other_options(self, val={}):
    ''' Pass other template-specific plot-level options (as a dictionary). '''
    self._global_opts['other'] = val

  def _set_units(self, prop, val):
    assert np.isscalar(val), '%s must be a scalar.' % prop
    self._global_opts[prop] = val

  def set_xunits(self, val=1):
    ''' Set a scaling factor by which the data is divided before plotting. '''
    self._set_units('xunits', val)
  def set_x2units(self, val=1):
    ''' Set a scaling factor by which the data is divided before plotting. '''
    self._set_units('x2units', val)
  def set_yunits(self, val=1):
    ''' Set a scaling factor by which the data is divided before plotting. '''
    self._set_units('yunits', val)
  def set_y2units(self, val=1):
    ''' Set a scaling factor by which the data is divided before plotting. '''
    self._set_units('y2units', val)
  def set_zunits(self, val=1):
    ''' Set a scaling factor by which the data is divided before plotting. '''
    self._set_units('zunits', val)

  def get_export_formats(self):
    '''Get the export formats supported by the template. '''
    cfg = self._read_config()
    return cfg['export-formats'].split()

  def set_export_format(self, val=None):
    ''' Set the desired export format (png, pdf, etc.) for generating an image of the plot.
        Call :meth:`get_export_formats` to see which formats your template supports. '''
    self._global_opts['export_format'] = val

  def set_show_on_screen(self, val=True):
    ''' Shown the output on screen (as opposed to only exporting to PNG/EPS/...).

        Calling this does not automatically execute the plot script.
        (Do it using :meth:`run` or directly from a shell.) '''
    assert isinstance(val, bool), 'show_on_screen must be set to True or False.'
    self._global_opts['show_on_screen'] = val

  def set_width(self, val=800):
    ''' Set plot width in pixels.'''
    assert int(val) > 10, 'width must be given in pixels'
    self._global_opts['width'] = int(val)

  def set_height(self, val=600):
    ''' Set plot height in pixels.'''
    assert int(val) > 10, 'height must be given in pixels'
    self._global_opts['height'] = int(val)

  def set_fontsize(self, val=None):
    ''' Set the "base" font size for axis labels etc.
      Templates usually scale this to a smaller value for ticks etc. '''
    assert val==None or val > 2, 'font size must be given in points.'
    self._global_opts['basefontsize'] = val

  def set_title(self, val=None):
    ''' Set the title of the plot window. '''
    assert val == None or isinstance(val, basestring), 'title must be a string'
    self._global_opts['title'] = val

  def set_legend(self, val=True):
    ''' Enable/disable legend.'''
    assert isinstance(val, bool), 'legend must be set to True or False.'
    self._global_opts['legend'] = val

  def set_xlabel(self, val=None):
    '''Set label for the left x axis.'''
    assert val == None or isinstance(val, basestring), 'xlabel must be a string'
    self._global_opts['xlabel'] = val

  def set_x2label(self, val=None):
    '''Set label for the right x axis.'''
    assert val == None or isinstance(val, basestring), 'x2label must be a string'
    self._global_opts['x2label'] = val

  def set_ylabel(self, val=None):
    '''Set label for the bottom y axis.'''
    assert val == None or isinstance(val, basestring), 'ylabel must be a string'
    self._global_opts['ylabel'] = val

  def set_y2label(self, val=None):
    '''Set label for the top y axis.'''
    assert val == None or isinstance(val, basestring), 'y2label must be a string'
    self._global_opts['y2label'] = val

  def set_zlabel(self, val=None):
    '''Set label for the z/color axis.'''
    assert val == None or isinstance(val, basestring), 'zlabel must be a string'
    self._global_opts['zlabel'] = val

  def set_cblabel(self, val=None):
    '''Set label for the z/color axis.'''
    assert val == None or isinstance(val, basestring), 'cblabel must be a string'
    self._global_opts['cblabel'] = val

  def set_xlog(self, val=False):
    '''Set log scale on the left x axis.'''
    assert isinstance(val, bool), 'xlog must be set to True or False.'
    self._global_opts['xlog'] = val

  def set_x2log(self, val=False):
    '''Set log scale on the right x axis.'''
    assert isinstance(val, bool), 'x2log must be set to True or False.'
    self._global_opts['x2log'] = val

  def set_ylog(self, val=False):
    '''Set log scale on the bottom y axis.'''
    assert isinstance(val, bool), 'ylog must be set to True or False.'
    self._global_opts['ylog'] = val

  def set_y2log(self, val=False):
    '''Set log scale on the top y axis.'''
    assert isinstance(val, bool), 'y2log must be set to True or False.'
    self._global_opts['y2log'] = val

  def set_zlog(self, val=False):
    '''Set log scale on the z/color axis.'''
    assert isinstance(val, bool), 'zlog must be set to True or False.'
    self._global_opts['zlog'] = val

  def set_xrange(self, minval=None, maxval=None):
    '''Set the bottom x axis range, None means auto.'''
    assert minval == None or np.isreal(minval), 'minval must be a real number.'
    assert maxval == None or np.isreal(maxval), 'maxval must be a real number.'
    self._global_opts['xrange'] = (minval, maxval)

  def set_x2range(self, minval=None, maxval=None):
    '''Set the top x axis range, None means auto.'''
    assert minval == None or np.isreal(minval), 'minval must be a real number.'
    assert maxval == None or np.isreal(maxval), 'maxval must be a real number.'
    self._global_opts['x2range'] = (minval, maxval)

  def set_yrange(self, minval=None, maxval=None):
    '''Set the left y axis range, None means auto.'''
    assert minval == None or np.isreal(minval), 'minval must be a real number.'
    assert maxval == None or np.isreal(maxval), 'maxval must be a real number.'
    self._global_opts['yrange'] = (minval, maxval)

  def set_y2range(self, minval=None, maxval=None):
    '''Set the right y axis range, None means auto.'''
    assert minval == None or np.isreal(minval), 'minval must be a real number.'
    assert maxval == None or np.isreal(maxval), 'maxval must be a real number.'
    self._global_opts['y2range'] = (minval, maxval)

  def set_zrange(self, minval=None, maxval=None):
    '''Set the z axis range, None means auto.'''
    assert minval == None or np.isreal(minval), 'minval must be a real number.'
    assert maxval == None or np.isreal(maxval), 'maxval must be a real number.'
    self._global_opts['zrange'] = (minval, maxval)

  def set_grid(self, val=True):
    '''Show grid lines.'''
    assert isinstance(val, bool), 'grid must be set to True or False.'
    self._global_opts['grid'] = val


  ##############
  #
  # Adding/updating/removing individual traces
  #
  ##############

  def add_trace(self, x, y=None, yerr=None,
                slowcoordinate=None,
                points=True, lines=False,
                skip=1,
                crop=0,
                title=None,
                pointtype=None, pointsize=None,
                linetype=None, linewidth=None,
                color=None,
                right=False,
                top=False,
                other=None,
                update=False,
                sort=None,
                x_plot_units=None, y_plot_units=None, # deprecated
              ):
    '''
    Add a 1D trace to the plot (or rather a 2D parametric curve).

    :param x,y:   the x and y coordinates as two separate vectors of length N or as a Nx2 or 2xN matrix
    :param yerr:  error bars for the ycoordinate
    :param slowcoordinate:  second coordinate as a single scalar for the whole trace, used only in some templates (e.g. 2D color maps)
    :param points:  draw points
    :param lines:  connect points with lines
    :param skip:  plot only every skip'th point
    :param crop:  leave out crop points at each end
    :param title:  label for this trace in a legend
    :param point/linetype:  integer indicating the point/line style (see gnuplot pointtypes)
    :param point/linesize:  size
    :param color:  point/line color
    :param right:  use the second y-axis (left = first y-axis)
    :param top:  use the second x-axis (bottom = first x-axis)
    :param other:  template-specific per-trace options (as a dictionary)
    :param update:  regenerate the plot script?
    :param sort:  if 'x' or 'y', sort the added points according to x or y first.
    :param x_plot_units:  **depracated**, use set_x_units()
    :param y_plot_units:  **depracated**, use set_y_units()

    :return: a unique identifier for the trace
    '''
    assert crop == None or isinstance(crop, int), 'crop must be an int'
    assert skip == None or isinstance(skip, int), 'skip must be an int'

    if x_plot_units != None: logging.warn('Passing x_plot_units to add_trace() is deprecated and does nothing. Use the plot-level set_xunits() instead.')
    if y_plot_units != None: logging.warn('Passing y_plot_units to add_trace() is deprecated and does nothing. Use the plot-level set_yunits() instead.')

    if slowcoordinate == 'auto' and title != None and len(title) > 0:
      # Attempt parsing the slow coordinate value from the trace title (if none was specified).
      m = re.findall(r'([e\d\.\+\-]+)', title)
      if len(m) == 1: # don't try to guess if multiple matches
        try:
          slowcoordinate = float(m[0])
          logging.info('Assuming %s in "%s" is a "slow coordinate". It will be used in multidimensional plots.', m[0], title)
        except:
          pass

    # Generate a random unique id for the trace
    trace_id = uuid.uuid4().hex

    self._traces[trace_id] = {
      'recordformat':[], # this is updated by update_trace() (called below)
      'yerrorcol':None, # this is updated by update_trace() (called below)
      'slowcoordinate':slowcoordinate,
      'points':points,
      'lines':lines,
      'skip':skip,
      'crop':crop,
      'title':title,
      'pointtype':pointtype,
      'pointsize':pointsize,
      'linetype':linetype,
      'linewidth':linewidth,
      'color':color,
      'right':right,
      'top':top,
      'other':other
      }

    # Generate the binary data file
    self.update_trace(trace_id, x, y, yerr, update=update, sort=sort)

    return trace_id

  def update_trace(self, trace_id, x, y=None, yerr=None, update=False, sort=None):
    '''
    Update data points of the specified trace.

    :param trace_id: the identifier returned by :meth:`add_trace`
    :param x,y,yerr:  see :meth:`add_trace`
    :param update:  regenerate the plot script?
    :param sort:  sort the values according to 'x' or 'y'

    Note: Trace options cannot be updated after the initial :meth:`add_trace`.
    '''

    # Convert the data to a two or three (if yerr!=none) column format

    trace = self._traces[trace_id]

    dd, yerr_column = self._convert_trace_input_to_list_of_tuples(x, y, yerr)

    if sort != None:
      if   sort == 'x':  m = dd[:,0].argsort()
      elif sort == 'y':  m = dd[:,1].argsort()
      else: raise Exception('Only "x" and "y" are valid options for sort. Got "%s".' % sort)
      dd = dd[m]
      if isinstance(yerr_column, np.ndarray): yerr_column = yerr_column[m]

    # Drop specified points
    crop = trace['crop']
    skip = trace['skip']
    if crop > 0 and len(data) > crop: dd = dd[crop:-crop]
    if skip > 1: dd = dd[::skip]

    trace_bytes = os.path.join(self.get_output_dir(), 'trace_%s.bytes' % trace_id)

    if len(dd) < 1:
      logging.warn('No points in the added/updated trace.')
      try: os.remove(trace_bytes)
      except: pass # normal if there was no previous version
    else:
      # Convert all inputs to float for simplicity.
      # Should not be a big problem for plotting purposes...
      if dd.dtype != np.float: dd = np.array(dd, dtype=np.float)

      # Use the default numpy binary format for output
      # Write to a temp file (.new) first and rename it once its complete.
      # This way the update is atomic from the point of view of
      # external programs that monitor changes to the file.
      dd.astype(np.float).tofile(trace_bytes + '.new')
      shutil.move(trace_bytes + '.new', trace_bytes)

      # Update the 'recordformat' field for the trace.
      _DATA_TYPES = {
        np.dtype('int8'): 'int8',
        np.dtype('int16'): 'int16',
        np.dtype('int32'): 'int32',
        np.dtype('int64'): 'int64',
        np.dtype('uint8'): 'uint8',
        np.dtype('uint16'): 'uint16',
        np.dtype('uint32'): 'uint32',
        np.dtype('uint64'): 'uint64',
        np.dtype('float32'): 'float32',
        np.dtype('float64'): 'float64',
        }
      # All columns currently have the same format...
      trace['recordformat'] = [ _DATA_TYPES[dd.dtype] for i in range(len(dd[0])) ]
      trace['yerrorcol'] = yerr_column

    if update: self.update()

  def remove_trace(self, trace_id, update=False):
    '''Remove the specified trace.

    :param trace_id: the identifier returned by :meth:`add_trace`
    :param update:  regenerate the plot script?
    '''
    if trace_id not in self._traces.keys():
      logging.warn('No trace %s in plot %d.', trace_id, self.get_name())
      return

    # delete the binary data file
    bin_path = os.path.join(self.get_output_dir(), 'trace_%s.bytes' % trace_id)
    try:
      os.remove(bin_path)
    except:
      # this can happen if the added trace was empty
      logging.debug('Could not remove %s.', bin_path)

    del self._traces[trace_id]

    if update: self.update()

  def get_ntraces(self, left=True, right=True):
    ''' Number of traces. Count trace on left and/or right y-axis.'''
    on_right_axis = np.array([ t['right']==True for t in self._traces.values() ], dtype=np.bool)
    n = 0
    if right: n += on_right_axis.sum()
    if left: n += (~on_right_axis).sum()
    return n

  ##############
  #
  # Internal helpers
  #
  ##############

  def _read_config(self):
    template_dir, template_name, template_ext = self.get_template()
    cfg = configparser.SafeConfigParser()
    cfg_path = os.path.join(template_dir, template_name + '.cfg')
    try:
      cfg.read(cfg_path)
      return dict(itertools.chain(
          cfg.items('general'),
          cfg.items('windows') if os.name == 'nt' else cfg.items('unix')
          ))
    except:
      logging.exception('Could not read the template config file %s.', cfg_path)
      raise


  def _get_helper_file_path(self, name):
    ''' Return a path as (full_path, file_part_only) to a file that matches one of:
     -- template_dir/name
     -- template_dir/*name
     -- common_helper_scripts/name
    '''
    if name=='' or name==None: raise Exception('Empty file name/extension.')

    template_dir, template_name, template_ext = self.get_template()

    src_path = os.path.join(template_dir, name)
    if os.path.exists(src_path): return src_path, name

    # look for a matching extension in the template dir
    for f in os.listdir(template_dir):
      if f.strip().endswith(name.strip()):
        src_path = os.path.join(template_dir, f)
        return src_path, f

    # look for a file in the common_helper_scripts dir
    src_path = os.path.join(self._common_helper_scripts_path, name)
    if os.path.exists(src_path): return src_path, name

    raise Exception('Could not find %s in the template dir or in the common_helper_scripts dir.' % name)


  def _convert_trace_input_to_list_of_tuples(self, x, y=None, yerr=None):
    '''
    Interpret input vectors/matrices and convert them to
    the standard internal [ (x0,y0), (x1,y1), ...] format.

    (This is a conscious violation of the "no guessing"
     principle mentioned in the class doc string.)
    '''

    complex_dtypes = [np.complex, np.complex64, np.complex128, np.complexfloating, np.complex_]
    try: complex_dtypes.append(np.complex256) # 64-bit systems only? (Or maybe a numpy version thing.)
    except AttributeError: pass

    # convert python lists to numpy arrays
    if not isinstance(x, np.ndarray): x = np.array(x)
    if (not isinstance(y, np.ndarray)) and y != None: y = np.array(y)
    if (not isinstance(yerr, np.ndarray)) and yerr != None: yerr = np.array(yerr)

    if len(x.shape) == 1:

      if x.dtype in complex_dtypes:
        assert y == None, 'x is complex so y must be None. Points described by a single complex vector will be plotted in the complex plane.'
        dd = np.array(( x.real, x.imag )).T
      else:
        assert isinstance(y, np.ndarray), 'y must be given if x is a real vector.'
        assert x.shape == y.shape, "x and y vector lengths don't match [%s vs %s]." % (x.shape, y.shape)
        if y.dtype in complex_dtypes:
          # interpret a real x + complex y as parametrized curve in the complex plane
          # with the parameter plotted along z.
          dd = np.array(( y.real, y.imag, x )).T
        else:
          dd = np.array(( x, y )).T

    elif len(x.shape) == 2:
      assert y == None, "If x is 2D matrix, y cannot be specified."
      assert x.dtype not in complex_dtypes, 'x must be real if x is a 2D matrix.'
      assert x.shape[0] in [2,3] or x.shape[1] in [2,3], "Input 2D matrix size is not 2xn, nx2, 3xn, or nx3. Don't know what you mean."
      if max(x.shape) > 3:
        dd = x if x.shape[0] >= x.shape[1] else x.T  # ensure that the shape is nx2
      else:
        logging.warn('Plotting a small matrix (%s). Cannot automatically determine whether it should be transposed or not. Assuming not', x.shape)
        dd = x

    else:
      raise Exception("Input matrix is more than 2D. Don't know how to interpret it.")

    if isinstance(yerr, np.ndarray) or yerr != None: # The first condition is here just to avoid a future warning about comparing ndarrays to None.
      yerr1d = np.zeros(len(dd), dtype=np.float) + np.nan
      try: # whether a single scalar
        yerr1d[:] = float(yerr)
      except: # or a 1D vector
        assert len(yerr) == len(dd), 'yerr must be a positive scalar or a vector of same length as x'
        assert len(yerr.shape) == 1, 'yerr must be a 1D (numpy) vector'
        assert (yerr < 0).max() == 0, 'components of yerr must be non-negative'
        yerr1d[:] = yerr
      dd = np.hstack(( dd, yerr1d.reshape((-1,1)) ))
      yerr_column = 2
    else:
      yerr_column = None

    return dd, yerr_column


  ######################################
  # For backwards compatibility.
  # Will be eventually removed entirely.
  ######################################
  def _set_ticks(self, axis, val):
    other = self._global_opts['other']
    other[axis + 'ticks'] = val

  def set_xticks(self, val=True, options=None):
    '''DEPRACATED: Enable/disable ticks on left x axis.'''
    logging.warn('set_xticks is depracated. Change ticks directly in the template or use set_other_options() ')
    self._set_ticks('x', val)
  def set_x2ticks(self, val=True, options=None):
    '''DEPRACATED: Enable/disable ticks on right x axis, or set to "mirror" for mirroring x1 ticks.'''
    self._set_ticks('x2', val)
  def set_yticks(self, val=True, options=None):
    '''DEPRACATED: Enable/disable ticks on bottom y axis.'''
    self._set_ticks('y', val)
  def set_y2ticks(self, val=True, options=None):
    '''DEPRACATED: Enable/disable ticks on top y axis, or set to "mirror" for mirroring y1 ticks.'''
    self._set_ticks('y2', val)
  def set_zticks(self, val=True, options=None):
    '''DEPRACATED: Enable/disable ticks on z axis.'''
    self._set_ticks('z', val)

  def set_export_png(self, val=True):
    ''' DEPRACATED: Export a PNG image of the plot.
        Some templates may export to another rasterized format or not support this at all. '''
    logging.warn('set_export_png is depracated. Replace with set_export_format("png")')
    self.set_export_format("png" if val else "")
  def set_export_eps(self, val=True):
    ''' DEPRACATED: Export an EPS image of the plot.
        Some templates may export to another vectorized format or not support this at all. '''
    logging.warn('set_export_eps is depracated. Replace with set_export_format("eps")')
    self.set_export_format("eps" if val else "")



# Add get functions for all global parameters
_attributes = dir(Plot)
for m in _attributes:
  if m.startswith('set_'):
    param_name = m[len('set_'):]

    def get_fn(self, name=param_name): return self._global_opts[name]
    get_fn.__name__ = 'get_%s' % (param_name)
    get_fn.__doc__ = 'Get %s. (See documentation for :meth:`set_%s` for details.)' % (param_name, param_name)

    if not (param_name in ['set_export_png', 'set_export_eps']
            or get_fn.__name__ in _attributes):
      setattr(Plot, get_fn.__name__, get_fn)
