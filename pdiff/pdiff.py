import argparse
import difflib
import os
import re
import sys

import argparse_extensions
import colorama
import six

from . import __version__
from . import terminal_util

_COLOR_RESET = colorama.Style.RESET_ALL
_COLOR_ADD = colorama.Fore.GREEN
_COLOR_DELETE = colorama.Fore.RED
_COLOR_CHANGE = colorama.Fore.MAGENTA
_COLOR_FILE_HEADER = colorama.Fore.BLUE
_COLOR_HUNK_HEADER = colorama.Fore.CYAN

_MARKER_COLORS = {
    '\x00+': _COLOR_ADD,
    '\x00-': _COLOR_DELETE,
    '\x00^': _COLOR_CHANGE,
    '\x01': _COLOR_RESET,
}


def colorize(text, color):
  return color + text + _COLOR_RESET


def get_hunks(mdiff):
  hunk = []

  for mdiff_tuple in mdiff:
    if mdiff_tuple[2] is None:
      if hunk:
        yield hunk
        hunk = []
    else:
      hunk.append(mdiff_tuple)

  # Don't forget the last hunk, which isn't followed by a context separator
  if hunk:
    yield hunk


def format_half_line(half_line, half_width):
  # Split `'foo\x1b[31mbar\x1b[0m'` into `['foo', '\x1b[31m', 'bar', '\x1b[0m']`
  parts = re.split('(\x1b\\[(?:0|[34][0-7])m)', half_line)
  visible_len = sum(len(part) for part in parts if not part.startswith('\x1b'))

  if visible_len <= half_width:
    half_lines = [half_line]
  else:
    half_lines = ['']
    visible_len = 0
    last_color = _COLOR_RESET

    # We can't simply wrap `half_line` at every `half_width` chars due to color
    # codes, so we manually assemble `half_lines` from `parts`
    for part in parts:
      if part.startswith('\x1b'):
        half_lines[-1] += part
        last_color = part
      elif visible_len + len(part) <= half_width:
        half_lines[-1] += part
        visible_len += len(part)
      else:
        first_offset = half_width - visible_len
        half_lines[-1] += part[:first_offset] + _COLOR_RESET

        for offset in range(first_offset, len(part), half_width):
          wrapped_half_line = part[offset:offset + half_width]
          half_lines.append(last_color + wrapped_half_line + _COLOR_RESET)
          visible_len = len(wrapped_half_line)

  # Always right pad the last half line
  pad_len = half_width - visible_len
  half_lines[-1] += ' ' * pad_len
  return half_lines


def format_line(old_line, new_line, width):
  half_width = width // 2 - 1
  empty_half = ' ' * half_width

  old_half_lines = format_half_line(old_line, half_width)
  new_half_lines = format_half_line(new_line, half_width)

  return '\n'.join(
      old_half + ' ' + new_half for old_half, new_half in six.moves.zip_longest(
          old_half_lines, new_half_lines, fillvalue=empty_half)) + '\n'


def format_file_header(old_filename, new_filename, width):
  old_header = colorize('--- ' + old_filename, _COLOR_FILE_HEADER)
  new_header = colorize('+++ ' + new_filename, _COLOR_FILE_HEADER)
  return format_line(old_header, new_header, width)


def format_hunk_header(hunk, width):
  old_nums = [old_num for (old_num, _), _, _ in hunk if old_num != '']
  new_nums = [new_num for _, (new_num, _), _ in hunk if new_num != '']
  old_start = old_nums[0] if old_nums else 0
  new_start = new_nums[0] if new_nums else 0
  old_header = colorize(
      '@@ -%d,%d @@' % (old_start, len(old_nums)), _COLOR_HUNK_HEADER)
  new_header = colorize(
      '@@ +%d,%d @@' % (new_start, len(new_nums)), _COLOR_HUNK_HEADER)
  return format_line(old_header, new_header, width)


def get_signs(old_line, new_line, has_changes):
  if not has_changes:
    return ' ', ' '
  elif not old_line:
    return ' ', colorize('+', _COLOR_ADD)
  elif not new_line:
    return colorize('-', _COLOR_DELETE), ' '
  else:
    return colorize('!', _COLOR_CHANGE), colorize('!', _COLOR_CHANGE)


def highlight_whitespace(line):
  # For whitespace-only diffs, change `\x1b[30m` to `\x1b[40m` (background)
  return re.sub('(?<=\x1b\\[)3(?=[0-7]m\\s+\x1b\\[0m)', '4', line)


def format_hunk(hunk, width, tab_size, signs):
  yield format_hunk_header(hunk, width)

  for (old_num, old_line), (new_num, new_line), has_changes in hunk:
    old_line = old_line.replace('\n', '').replace('\t', ' ' * tab_size)
    new_line = new_line.replace('\n', '').replace('\t', ' ' * tab_size)

    if has_changes:
      for marker, color in _MARKER_COLORS.items():
        old_line = old_line.replace(marker, color)
        new_line = new_line.replace(marker, color)

      if old_line and new_line:
        old_line = highlight_whitespace(old_line)
        new_line = highlight_whitespace(new_line)

    if signs:
      old_sign, new_sign = get_signs(old_line, new_line, has_changes)
      old_line = old_sign + old_line
      new_line = new_sign + new_line

    yield format_line(old_line, new_line, width)


def pdiff(old_filename, new_filename, context, width, tab_size, signs):
  # `readlines` because `difflib._mdiff` can't operate on a generator
  with open(old_filename, 'r') as old_file:
    old_lines = old_file.readlines()

  with open(new_filename, 'r') as new_file:
    new_lines = new_file.readlines()

  yield format_file_header(old_filename, new_filename, width)

  mdiff = difflib._mdiff(old_lines, new_lines, context=context)

  # `mdiff` context separators don't have the metadata necessary to generate
  # git-diff-like hunk headers (`@@ -%d,%d @@` and `@@ +%d,%d @@`), so we
  # partition `mdiff` into hunks and process each one separately
  for hunk in get_hunks(mdiff):
    for line in format_hunk(hunk, width, tab_size, signs):
      yield line


def main():
  parser = argparse.ArgumentParser(
      usage='%(prog)s [<options>] [--] <old-file> <new-file>',
      description='Pretty side-by-side diff')

  parser.add_argument(
      'old_filename',
      help=argparse.SUPPRESS,
      metavar='<old-file>')
  parser.add_argument(
      'new_filename',
      help=argparse.SUPPRESS,
      metavar='<new-file>')

  parser.add_argument(
      '-v',
      '--version',
      action='version',
      version='%(prog)s ' + __version__)
  parser.add_argument(
      '--expand-tabs',
      dest='tab_size',
      type=int,
      default=8,
      help='expand tabs to %(metavar)s spaces; default: %(default)s',
      metavar='<n>')
  parser.add_argument(
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
      '--width',
      type=int,
      default=None,
      help='fit output to %(metavar)s columns; default: autodetect',
      metavar='<n>')

  args = parser.parse_args()

  if args.width is None:
    args.width = terminal_util.get_terminal_size().columns

  for filename in (args.old_filename, args.new_filename):
    if not os.path.exists(filename):
      sys.stderr.write('error: file does not exist: %s\n' % filename)
      return 1
    elif os.path.isdir(filename):
      sys.stderr.write('error: path is a directory: %s\n' % filename)
      return 1

  for line in pdiff(
      args.old_filename,
      args.new_filename,
      args.context,
      args.width,
      args.tab_size,
      args.signs):
    sys.stdout.write(line)

  return 0


if __name__ == '__main__':
  sys.exit(main())
