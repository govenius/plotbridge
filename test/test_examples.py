#!/usr/bin/python

import unittest
import shutil
import tempfile
import logging
import os
import subprocess
import re
import difflib

def _get_references_to_bytes(gnuplot_file, is_file=True):
  ''' Return all of the references to .bytes files in the specified .gnuplot file. '''
  if is_file:
    with open(gnuplot_file, 'r') as f:
      gnuplot_file = f.read()

  refs = re.findall(r'(?ims)(trace_[0123456789abcdef]{32}\.bytes)', gnuplot_file)
  # return only the first ref to each file
  return [ r for i,r in enumerate(refs) if r not in refs[:i] ]

output_dirs_pending_deletion = []

class TestExamples(unittest.TestCase):
  delete_output_after_test = False

  def setUp(self):
    self._test_dir = tempfile.mkdtemp(prefix='plotbridge_test_')

  def tearDown(self):
    #logging.warn('Removing %s', self._test_dir)
    if TestExamples.delete_output_after_test: shutil.rmtree(self._test_dir)
    else: output_dirs_pending_deletion.append(self._test_dir)

  def _test_gnuplot_example(self, example_name):
    shutil.copytree(os.path.join('..', 'examples', example_name),
                    os.path.join(self._test_dir, example_name))

    original_dir = os.path.abspath('.')
    exec_dir = os.path.abspath(os.path.join(self._test_dir, example_name))
    try:
      os.chdir(exec_dir)

      files_before_execution = os.listdir('.')
      process = subprocess.Popen([ 'python', example_name[len('gnuplot_'):] + '.py' ],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 encoding='utf-8',
                                 cwd=exec_dir)
      process.wait()
      self.assertEqual(process.returncode, 0)

      # get the output directory name
      files_after_execution = os.listdir('.')
      self.assertEqual(len(files_after_execution), len(files_before_execution) + 1)
      output_dir = set(files_after_execution) - set(files_before_execution)
      for f in output_dir: output_dir = f

      # compare the files in the output and expected_output dirs
      expected_output_dir = 'expected_output'
      expected_files = os.listdir(expected_output_dir)
      output_files = os.listdir(output_dir)

      bytes_files_expected = [f for f in expected_files if (f.endswith('.bytes') and f.startswith('trace_')) ]
      bytes_files_output = [f for f in output_files if (f.endswith('.bytes') and f.startswith('trace_')) ]
      self.assertEqual(len(bytes_files_expected), len(bytes_files_output))

      gnuplot_file = [f for f in expected_files if f.endswith('.gnuplot') ]
      self.assertEqual(len(gnuplot_file), 1)
      gnuplot_file = gnuplot_file[0]
      self.assertTrue(os.path.isfile(os.path.join(output_dir, gnuplot_file)))

      bytes_refs_expected = _get_references_to_bytes(os.path.join(expected_output_dir, gnuplot_file))
      bytes_refs_output = _get_references_to_bytes(os.path.join(output_dir, gnuplot_file))
      self.assertEqual(len(bytes_refs_expected), len(bytes_refs_output))

      self.assertEqual(set(bytes_refs_output), set(bytes_files_output))

      # compare the contents of the .gnuplot files
      with open(os.path.join(expected_output_dir, gnuplot_file), 'r') as f:
        gnuplot_expected_str = f.read()
      for ref0, ref1 in zip(bytes_refs_expected, bytes_refs_output):
        gnuplot_expected_str = gnuplot_expected_str.replace(ref0, ref1)

      with open(os.path.join(output_dir, gnuplot_file), 'r') as f:
        gnuplot_output_str = f.read()

      n_differences = 0
      d = difflib.unified_diff(gnuplot_expected_str.split('\n'),
                                    gnuplot_output_str.split('\n'),
                                    'expected', 'output', lineterm='')

      # difflib just returns a bunch of lines.
      # Split them into deltas manually, mainly in order to ignore changes
      # in the number of empty lines.
      delta = []
      stop = False
      header_lines_to_skip = 2 # skip the "--- expected" and "+++ output" lines
      while not stop:
        try: l = next(d)
        except StopIteration:
          stop = True; l = None
        if header_lines_to_skip > 0:
          header_lines_to_skip -= 1; continue

        if stop or l.startswith('@@'):
          if len(delta) > 0:
            # previous delta has been fully read
            differing_lines = [ l for l in delta[3:] if l[:1] in ['+', '-'] and l.strip() not in ['+', '-'] ] # ignore changes to empty lines
            if len(differing_lines) > 0:
              n_differences += 1
              print('')
              print('\n'.join(delta))

          delta = [ l ]
        else:
          delta.append(l)

      self.assertEqual(n_differences, 0)

      # compare the contents of the .bytes files
      for e, o in zip(bytes_refs_expected, bytes_refs_output):
        with open(os.path.join(expected_output_dir, e), 'rb') as f_e:
          with open(os.path.join(output_dir, o), 'rb') as f_o:
            # This could fail if the byte orders are different on the
            # systems that generated the output and the
            # expected_output dirs.
            self.assertEqual(f_o.read(), f_e.read())

    finally:
      os.chdir(original_dir)


gnuplot_examples = [ 'gnuplot_minimal', 'gnuplot_basic1', 'gnuplot_basic2', 'gnuplot_histogram',
                     'gnuplot_with_direction', 'gnuplot_curve_in_3d', 'gnuplot_heatmap' ]

# Add test for all gnuplot examples
for e in gnuplot_examples:
  test_fn = lambda self, example=e: self._test_gnuplot_example(example)
  test_fn.__name__ = 'test_%s' % (e)
  test_fn.__doc__ = 'Test the %s example.' % (e)
  setattr(TestExamples, test_fn.__name__, test_fn)

if __name__ == '__main__':
  unittest.main(exit=False)

  import sys
  print ('\nTests finished.\nPress enter to delete the plots generated '
         'in the process: %s' % output_dirs_pending_deletion)
  sys.stdin.read(1)
  for d in output_dirs_pending_deletion:
    shutil.rmtree(d)
