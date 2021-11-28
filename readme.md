# pddgnimi

### "Put DuckDuckGo News In My Inbox"

This thing should scrape news articles from [DuckDuckGo](https://duckduckgo.com/) for a search query and send the output to an email. It's intended to be invoked as a cronjob or something so as to get hits on a news topic once a day.

**Under development!**

`develop` branch is fiddling, and this thing probably doesn't work as well as it should... It's the first thing I've ever written in Python...

You've been warned! ;)


## Installation

### Dependencies

- [elemental](https://github.com/red-and-black/elemental)
- [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) for Firefox
- `html5lib` for parsing HTML
- `htmlmin` for minifying HTML
- `bs4` BeautifulSoup to prettify HTML


```bash
# may need to install python package manager
sudo apt update && sudo apt install python3-pip

# install dependencies
pip install elemental html5lib htmlmin bs4

# install latest geckodriver for firefox from https://github.com/mozilla/geckodriver/releases/latest
# put it somewhere like /usr/bin or something else from $PATH
wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
sudo tar -xf geckodriver-v0.30.0-linux64.tar.gz --directory /usr/bin/
```

### Mail Server Settings

Open the `emailSettings.py` settings file and edit it to specify the SMTP server to use to send email alerts with.

Should be something like:

```python
mailserverHost = 'smtp.somewhere.com'
mailserverPort = '465'
mailserverUser = 'authaddress@somewhere.com'
mailserverPass = 'PasswordGoesHere'
```

## Usage

```
python3 pddgnimi.py "foo bar" emailaddress@somewhere.com
```

Where `foo bar` is your search query, and `emailaddress@somewhere.com` is the address to send the alert to.
