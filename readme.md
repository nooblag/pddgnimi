# pddgnimi

"Put DuckDuckGo News In My Inbox"

**Under development!**

`develop` branch is fiddling, and this thing probably doesn't work as well as it should... It's the first thing I've ever written in Python...

You've been warned! ;)


## Installation

### Dependencies

- [elemental](https://github.com/red-and-black/elemental)
- [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) if using Firefox w/ GUI?
- `html5lib` for parsing HTML
- `htmlmin` for minifying HTML
- `bs4` `BeautifulSoup4` to prettify HTML


```
# may need to install python package manager
sudo apt update && sudo apt install python3-pip

# install dependencies
pip install elemental html5lib htmlmin bs4 BeautifulSoup4

# may also need to do this? if this error occurs?
# ERROR: pyopenssl 21.0.0 has requirement cryptography>=3.3, but you'll have cryptography 2.8 which is incompatible.
pip install --upgrade cryptography

# install latest geckodriver for firefox from https://github.com/mozilla/geckodriver/releases/latest
# put it somewhere like /usr/bin or something else from $PATH
wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
sudo tar -xf geckodriver-v0.30.0-linux64.tar.gz --directory /usr/bin/
```

## Usage

```
python3 pddgnimi.py "foo bar"
```

Where `foo bar` is your search query.
