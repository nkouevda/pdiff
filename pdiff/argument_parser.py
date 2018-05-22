import argparse

import argparse_extensions

from . import __version__
from . import terminal_util


def get_parser():
  parser = argparse.ArgumentParser(
      usage='%(prog)s [<options>] [--] <old file> <new file>',
      description='Pretty side-by-side diff')

  parser.add_argument(
      'old_filename',
      type=str,
      help=argparse.SUPPRESS,
      metavar='<old file>')
  parser.add_argument(
      'new_filename',
      type=str,
      help=argparse.SUPPRESS,
      metavar='<new file>')

  parser.add_argument(
      '-t',
      '--expand-tabs',
      dest='tab_size',
      type=int,
      default=8,
      help='expand tabs to %(metavar)s spaces; default: %(default)s',
      metavar='<n>')
  parser.add_argument(
      '-S',
      '--signs',
      action=argparse_extensions.NegatableStoreTrueAction,
      default=True,
      help='show sign columns; default: %(default)s')
  parser.add_argument(
      '-U',
      '--unified',
      dest='context',
      type=int,
      default=3,
      help='show %(metavar)s lines of context; default: %(default)s',
      metavar='<n>')
  parser.add_argument(
      '-v',
      '--version',
      action='version',
      version='%(prog)s ' + __version__)
  parser.add_argument(
      '-W',
      '--width',
      type=int,
      default=terminal_util.get_terminal_size().columns,
      help='fit output to %(metavar)s columns; default: autodetect',
      metavar='<n>')

  return parser
