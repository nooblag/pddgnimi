# pddgnimi

### "Put DuckDuckGo News In My Inbox"

This thing should scrape news articles from [DuckDuckGo](https://duckduckgo.com/) for a search query in Australia and send the results to you in an e-mail. It's intended to be invoked as a cronjob so as to get hits on a news topic at intervals of your choosing.

For example, here's a "past day" e-mail alert for "celebrity news":

![Screenshot from 2022-01-13 00-37-40](https://user-images.githubusercontent.com/1122344/149153711-45f59e5a-a77e-487e-ad7f-8bc014a01d7b.png)



## Installation

Clone this repo, and jump into it:

```bash
git clone https://github.com/nooblag/pddgnimi.git
cd pddgnimi
```

Start **pddgnimi** to check that your system has the required software ready, and to save the details for the SMTP server that will be used later to send out all your e-mail alerts:

```bash
python3 pddgnimi.py
```

**pddgnimi** will save a successful configuration into `.settings.conf` so that the SMTP login is available/persistent between reboots. The configuration is locked (chmod 400) during set-up so that its contents are only be readable from within your user account (or by root).

_Note:_ The mailserver password is not encrypted in the configuration file (it's obfuscated, but that's small comfort) so be aware not to use a sensitive account!!!



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
