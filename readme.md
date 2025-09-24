# pddgnimi

### "Put DuckDuckGo News In My Inbox"

This thing should scrape news articles from [DuckDuckGo](https://duckduckgo.com/) for a search query in Australia and send the results to you in an e-mail. It's intended to be invoked as a cronjob so as to get hits on a news topic at intervals of your choosing.

For example, here's a "past day" e-mail alert for "celebrity news":

![Screenshot from 2022-01-13 00-37-40](https://user-images.githubusercontent.com/1122344/149153711-45f59e5a-a77e-487e-ad7f-8bc014a01d7b.png)



## Installation

1. Ensure required packages are available:

   ```bash
   sudo apt update
   sudo apt install git python3 python3-venv python3-pip
   ```

2. Clone this repo, and enter it:

   ```bash
   git clone https://github.com/nooblag/pddgnimi.git
   cd pddgnimi
   ```

3. Create a virtual environment for **pddgnimi** called `venv` and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the Python dependencies inside the venv:

   ```bash
   pip3 install -r requirements.txt
   ```

5. Download the latest [geckodriver](https://github.com/mozilla/geckodriver/) and put it with the venv binaries:

   ```bash
   wget --directory-prefix=venv/bin https://github.com/mozilla/geckodriver/releases/download/version/geckodriver-version-linux-arch.tar.gz
   tar --extract --file=venv/bin/geckodriver-version-linux-arch.tar.gz --directory=venv/bin
   chmod +x venv/bin/geckodriver
   ```

   where `version` and `arch` are of course replaced with the proper hoohaa, and verify that went well:

   ```bash
   venv/bin/geckodriver --version
   ```

6. Escalate to superuser and set up **pddgnimi** as a systemd timer, by copying over the templates:

   ```bash
   sudo cp etc/systemd/system/pddgnimi.timer etc/systemd/system/pddgnimi.service /etc/systemd/system/
   ```

   and modify the paths and environment variables in the `pddgnimi.service` file:

   ```ini
   [Service]
   ExecStart=/path/to/pddgnimi/venv/bin/python3 /path/to/pddgnimi/pddgnimi.py
   WorkingDirectory=/path/to/pddgnimi
   Environment="pddgnimi_smtp_host=example.com"
   Environment="pddgnimi_smtp_port=465"
   Environment="pddgnimi_smtp_user=this@example.com"
   Environment="pddgnimi_smtp_pass=123456qwerty"
   ```

   where `/path/to/pddgnimi` is the path where you cloned this repo.

   Can also modify the run schedule by editing the `pddgnimi.timer` file at this step.

7. Edit list of queries to run on schedule by adding them to `config/search.list`.

8. Reload the systemd configs to recognise the new **pddgnimi** units:

   ```bash
   sudo systemctl daemon-reload
   ```

   and enable, with:

   ```bash
   sudo systemctl enable pddgnimi.timer
   ```

9. Start the timer, and we're off!

    ```bash
    sudo systemctl start pddgnimi.timer
    ```

<br>


## Usage

**pddgnimi** can be invoked from the command line:

```bash
source venv/bin/activate
export pddgnimi_smtp_host='mail.example.com'
export pddgnimi_smtp_port='123'
export pddgnimi_smtp_user='sender@example.com'
export pddgnimi_smtp_pass='smtpuserpass123'
python3 pddgnimi.py
```

<br>


### Changing Scope

Narrowing results from a the past day or past week or past month or from any time can be specified for each query specified in `config/search.list`. For example, for alerts of news from the past week:

```
football --scope=week --email=alertaddress@example.com
```

Acceptable arguments for scope are: `day` `week` `month` `any`

If no argument is specified, the default is to scrape news articles from `any` time.
