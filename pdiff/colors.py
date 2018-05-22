import colorama

RESET = colorama.Style.RESET_ALL
ADD = colorama.Fore.GREEN
DELETE = colorama.Fore.RED
CHANGE = colorama.Fore.MAGENTA
FILE_HEADER = colorama.Fore.BLUE
HUNK_HEADER = colorama.Fore.CYAN

MARKERS = {
    '\x00+': ADD,
    '\x00-': DELETE,
    '\x00^': CHANGE,
    '\x01': RESET,
}


def colorize(text, color):
  return color + text + RESET
