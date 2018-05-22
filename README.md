# pdiff

Pretty side-by-side diff.

Inspired by [`cdiff`](https://github.com/ymattw/cdiff) and
[`icdiff`](https://github.com/jeffkaufman/icdiff).

## Installation

    pip install pdiff

## Usage

```
usage: pdiff [<options>] [--] <old file> <new file>

Pretty side-by-side diff

optional arguments:
  -h, --help            show this help message and exit
  -t <n>, --expand-tabs <n>
                        expand tabs to <n> spaces; default: 8
  -S, --signs, --no-signs
                        show sign columns; default: True
  -U <n>, --unified <n>
                        show <n> lines of context; default: 3
  -v, --version         show program's version number and exit
  -W <n>, --width <n>   fit output to <n> columns; default: autodetect
```

### Git

Configure a `pdiff` `difftool`, and add some aliases to your liking, e.g.:

```
[difftool.pdiff]
	cmd = "pdiff -- \"$LOCAL\" \"$REMOTE\" | less -R"

[alias]
	dfp = difftool --tool=pdiff
	dfpc = difftool --tool=pdiff --cached
```

## License

[MIT License](LICENSE.txt)
