# pddgnimi

"Put DuckDuckGo In My Inbox"


## Usage

### Install dependencies

- pip
- [elemental](https://github.com/red-and-black/elemental)
- [geckodriver](https://github.com/mozilla/geckodriver/releases/latest)


```
# may need to install python package manager
sudo apt update && sudo apt install python3-pip

# elemental https://github.com/red-and-black/elemental
pip install elemental

# may also need to do this? if this error occurs?
# ERROR: pyopenssl 21.0.0 has requirement cryptography>=3.3, but you'll have cryptography 2.8 which is incompatible.
pip install --upgrade cryptography

# install latest geckodriver for firefox from https://github.com/mozilla/geckodriver/releases/latest
# put it somewhere like /usr/bin or something else from $PATH
wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
sudo tar -xf geckodriver-v0.30.0-linux64.tar.gz --directory /usr/bin/
```

### Fire up Python3
