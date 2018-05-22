import difflib
import re

import six

from . import colors


class DiffFormatter(object):

  OLD_HEADER_PREFIX = '--- '
  NEW_HEADER_PREFIX = '+++ '
  OLD_HUNK_HEADER_TEMPLATE = '@@ -%d,%d @@'
  NEW_HUNK_HEADER_TEMPLATE = '@@ +%d,%d @@'

  def __init__(
      self, old_filename, new_filename, context, width, tab_size, signs):
    self.old_filename = old_filename
    self.new_filename = new_filename
    self.context = context
    self.width = width
    self.tab_size = tab_size
    self.signs = signs

    self.half_width = self.width // 2 - 1
    self.empty_half = ' ' * self.half_width
    self.tab_spaces = ' ' * self.tab_size

  def get_lines(self):
    # `readlines` because `difflib._mdiff` can't operate on a generator
    with open(self.old_filename, 'r') as old_file:
      old_lines = old_file.readlines()
    with open(self.new_filename, 'r') as new_file:
      new_lines = new_file.readlines()

    yield self._format_file_header()

    mdiff = difflib._mdiff(old_lines, new_lines, context=self.context)

    # `mdiff` context separators don't have the metadata necessary to generate
    # git-diff-like hunk headers (`@@ -%d,%d @@` and `@@ +%d,%d @@`), so we
    # partition `mdiff` into hunks and process each one separately
    for hunk in self._get_hunks(mdiff):
      for line in self._format_hunk(hunk):
        yield line

  def _format_file_header(self):
    old_header = colors.colorize(
        DiffFormatter.OLD_HEADER_PREFIX + self.old_filename, colors.FILE_HEADER)
    new_header = colors.colorize(
        DiffFormatter.NEW_HEADER_PREFIX + self.new_filename, colors.FILE_HEADER)
    return self._format_line(old_header, new_header)

  def _get_hunks(self, mdiff):
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

  def _format_hunk(self, hunk):
    yield self._format_hunk_header(hunk)

    for (old_num, old_half), (new_num, new_half), has_changes in hunk:
      old_half = old_half.replace('\n', '').replace('\t', self.tab_spaces)
      new_half = new_half.replace('\n', '').replace('\t', self.tab_spaces)

      if has_changes:
        for marker, color in colors.MARKERS.items():
          old_half = old_half.replace(marker, color)
          new_half = new_half.replace(marker, color)

        if old_half and new_half:
          old_half = self._highlight_whitespace(old_half)
          new_half = self._highlight_whitespace(new_half)

      if self.signs:
        old_sign, new_sign = self._format_signs(old_half, new_half, has_changes)
        old_half = old_sign + old_half
        new_half = new_sign + new_half

      yield self._format_line(old_half, new_half)

  def _format_hunk_header(self, hunk):
    old_nums = [old_num for (old_num, _), _, _ in hunk if old_num != '']
    new_nums = [new_num for _, (new_num, _), _ in hunk if new_num != '']
    old_start = old_nums[0] if old_nums else 0
    new_start = new_nums[0] if new_nums else 0
    old_header = colors.colorize(
        DiffFormatter.OLD_HUNK_HEADER_TEMPLATE % (old_start, len(old_nums)),
        colors.HUNK_HEADER)
    new_header = colors.colorize(
        DiffFormatter.NEW_HUNK_HEADER_TEMPLATE % (new_start, len(new_nums)),
        colors.HUNK_HEADER)
    return self._format_line(old_header, new_header)

  def _highlight_whitespace(self, line):
    # For whitespace-only diffs, change `\x1b[30m` to `\x1b[40m` (background)
    return re.sub('(?<=\x1b\\[)3(?=[0-7]m\\s+\x1b\\[0m)', '4', line)

  def _format_signs(self, old_half, new_half, has_changes):
    if not has_changes:
      return ' ', ' '
    elif not old_half:
      return ' ', colors.colorize('+', colors.ADD)
    elif not new_half:
      return colors.colorize('-', colors.DELETE), ' '
    else:
      return (colors.colorize('!', colors.CHANGE),) * 2

  def _format_line(self, old_half, new_half):
    old_half_lines = self._format_half_lines(old_half)
    new_half_lines = self._format_half_lines(new_half)

    return '\n'.join(
        old_half + ' ' + new_half
        for old_half, new_half in six.moves.zip_longest(
            old_half_lines, new_half_lines, fillvalue=self.empty_half)) + '\n'

  def _format_half_lines(self, half_line):
    # Split `'ab\x1b[31mcd\x1b[0m'` into `['ab', '\x1b[31m', 'cd', '\x1b[0m']`
    parts = re.split('(\x1b\\[(?:0|[34][0-7])m)', half_line)
    visible_len = sum(
        len(part) for part in parts if not part.startswith('\x1b'))

    if visible_len <= self.half_width:
      half_lines = [half_line]
    else:
      half_lines = ['']
      visible_len = 0
      last_color = colors.RESET

      # We can't simply wrap `half_line` at every `half_width` chars due to
      # color codes, so we manually assemble `half_lines` from `parts`
      for part in parts:
        if part.startswith('\x1b'):
          half_lines[-1] += part
          last_color = part
        elif visible_len + len(part) <= self.half_width:
          half_lines[-1] += part
          visible_len += len(part)
        else:
          first_offset = self.half_width - visible_len
          half_lines[-1] += part[:first_offset] + colors.RESET

          for offset in range(first_offset, len(part), self.half_width):
            wrapped_half_line = part[offset:offset + self.half_width]
            half_lines.append(
                last_color + wrapped_half_line + colors.RESET)
            visible_len = len(wrapped_half_line)

    # Always right pad the last half line
    pad_len = self.half_width - visible_len
    half_lines[-1] += ' ' * pad_len
    return half_lines
