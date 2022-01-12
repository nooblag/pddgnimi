# pddgnimi

### "Put DuckDuckGo News In My Inbox"

This thing should scrape news articles from [DuckDuckGo](https://duckduckgo.com/) for a search query in Australia and send the results to you in an e-mail. It's intended to be invoked as a cronjob so as to get hits on a news topic at intervals of your choosing.

For example, here's an e-mail alert for "celebrity news":

![Screenshot from 2022-01-13 00-37-40](https://user-images.githubusercontent.com/1122344/149153711-45f59e5a-a77e-487e-ad7f-8bc014a01d7b.png)



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

### Configuration

Start the script for the first time to set up the details for the SMTP server that will be used to send your e-mail alerts.

```bash
python3 pddgnimi.py
```

The script will then save that configuration into `./settings.conf` so it is persistent between reboots, and only accessible to the user running the cronjob.


## Usage

**pddgnimi** is intended to be invoked from the command line, as follows:

```bash
python3 pddgnimi.py "foo bar" emailaddress@somewhere.com
```

Where `foo bar` is your search query, and `emailaddress@somewhere.com` is the address to send the alert to.


### Changing Scope

Narrowing results from a the past day or past week or past month or from any time can be specified as the second argument. For example, for alerts of news from the past week:

```bash
python3 pddgnimi.py "foo bar" week emailaddress@somewhere.com
```

Acceptable arguments for scope are: `day` `week` `month` `any`

If no argument is specified, the default is to scrape news articles from the past `day`
