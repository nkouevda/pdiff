# pdiff

Pretty side-by-side diff.

Inspired by [`ydiff`](https://github.com/ymattw/ydiff) and
[`icdiff`](https://github.com/jeffkaufman/icdiff).

## Example

![pdiff.png](https://github.com/nkouevda/images/raw/master/pdiff.png)

## Installation

    pip install pdiff

Or:

    brew install nkouevda/nkouevda/pdiff

## Usage

```
usage: pdiff [<options>] [--] <old file> <new file>

Pretty side-by-side diff

optional arguments:
  -h, --help            show this help message and exit
  -b, --background, --no-background
                        highlight background instead of foreground (default: True)
  -l, --line-numbers, --no-line-numbers
                        show line number columns (default: True)
  -t <n>, --expand-tabs <n>
                        expand tabs to <n> spaces (default: 8)
  -s, --signs, --no-signs
                        show sign columns (default: True)
  -U <n>, --unified <n>
                        show <n> lines of context (default: 3)
  -v, --version         show program's version number and exit
  -w <n>, --width <n>   fit output to <n> columns (default: autodetect)
```

### Git

Configure a `pdiff` `difftool`, and add some aliases to your liking, e.g.:

```
[difftool "pdiff"]
	cmd = "pdiff -- \"$LOCAL\" \"$REMOTE\" | less --Raw-control-chars"

[alias]
	dfp = difftool --tool=pdiff
	dfpc = difftool --tool=pdiff --cached
```

## License

[MIT License](LICENSE.txt)
