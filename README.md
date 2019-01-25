# RuuviTag
> A simple and clean Python library for [RuuviTag](https://ruuvi.com/ruuvitag-specs/)

## Installation
As the library is based on [bluepy](https://github.com/IanHarvey/bluepy),
compilation of `bluepy-helper` is required. This requires `glib2` development
packages.

On Debian-based systems the installation goes a bit like:

```sh
sudo apt-get install libglib2.0-dev
pip install git+https://github.com/kipe/ruuvitag.git
```

## Usage
For basic usage, you can just run `RuuviTag.scan()` in a loop, like this:

```python
from ruuvitag import RuuviTag

while True:
    for tag in RuuviTag.scan():
        print(tag)
```

For more complicated examples including threading, and motion detection,
see `examples` directory.
