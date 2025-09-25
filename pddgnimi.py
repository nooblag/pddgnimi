#!/usr/bin/python3


### REQUISITES ###

import os # files
import random # for sleep wait times
import re
import smtplib # for SMTP connection
import sys # stdout, stderr, env vars and non-zero exits
import traceback
import validators # beta package to test domains and email addresses
from bs4 import BeautifulSoup # prettify search results
from email.mime.multipart import MIMEMultipart # for HTML e-mails
from email.mime.text import MIMEText # for HTML e-mails
from selenium.common.exceptions import NoSuchElementException as element_not_found
from selenium.common.exceptions import TimeoutException as website_timeout
from selenium import webdriver # browser
from selenium.webdriver.common.by import By # find things by id, name, etc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.firefox.service import Service as geckodriver
from time import sleep # used to slow things down even more



### CONFIG ###

# [paths]
# get full path where this script is
working_directory=os.path.dirname(os.path.abspath(__file__))
config_directory=os.path.join(working_directory, 'config')
# browser
geckodriver_path=os.path.join(working_directory, 'venv', 'bin', 'geckodriver')
firefox_path='/usr/bin/firefox'

# [environment variables and required files]
config={
  'pddgnimi_smtp_host': os.getenv('pddgnimi_smtp_host'),
  'pddgnimi_smtp_port': os.getenv('pddgnimi_smtp_port'),
  'pddgnimi_smtp_user': os.getenv('pddgnimi_smtp_user'),
  'pddgnimi_smtp_pass': os.getenv('pddgnimi_smtp_pass'),
  'file_queries': os.path.join(config_directory, 'search.list'),
  'file_css_template': os.path.join(working_directory, 'style.css')
}

config_parsed=True # set up test
# any missing environment variables
failed_config=[key for key, setting in config.items() if setting is None]
# any missing/empty files
failed_files=[
  setting for key, setting in config.items()
  if key.startswith('file_') and (
    not os.path.isfile(config[key]) or
    os.path.getsize(config[key]) == 0
  )
]

if failed_config:
  print(f"Environment variables: These are missing/empty: {", ".join(failed_config)}.", file=sys.stderr)
  sys.exit(1) # always crash here
if failed_files:
  print(f"Required files: These files are missing/empty:\n  {"\n  ".join(failed_files)}", file=sys.stderr)
  config_parsed=False

if not validators.domain(config['pddgnimi_smtp_host']):
  print(f"Environment variables: pddgnimi_smtp_host '{config['pddgnimi_smtp_host']}' doesn't appear to a valid domain.", file=sys.stderr)
  config_parsed=False

# check port must be a number and in valid range
if not config['pddgnimi_smtp_port'].isdigit() or not 0 <= int(config['pddgnimi_smtp_port']) <= 65535:
  print("Environment variables: pddgnimi_smtp_port must be in the range 0-65535.", file=sys.stderr)
  config_parsed=False

# check if geckodriver binary is available
if not os.path.exists(geckodriver_path) or not os.access(geckodriver_path, os.X_OK):
  print("Required files: 'geckodriver' is not properly configured.", file=sys.stderr)
  config_parsed=False

# check if firefox is available
if not os.path.exists(firefox_path) or not os.access(firefox_path, os.X_OK):
  print("Required files: Firefox is not properly configured/installed.", file=sys.stderr)
  config_parsed=False

if not config_parsed: sys.exit(1)

# [scraper]
# set up browser
browser_options=firefox_options()
# set these below to make explicit handling for where selenium can't do the trick automatically
# like on arm64 for example, where selenium doesn't bundle geckodriver
browser_options.binary_location=firefox_path
browser_service=geckodriver(geckodriver_path)
browser_options.add_argument("--headless")
# always default to a big desktoppy type viewport
browser_options.add_argument('--window-size=1280x1024')
output_html=os.path.join(working_directory, '.output.html')

# [smtp]
# test the mail server connection and credentials
try:
  smtp_server=smtplib.SMTP_SSL(config['pddgnimi_smtp_host'], config['pddgnimi_smtp_port'])
  smtp_server.login(config['pddgnimi_smtp_user'], config['pddgnimi_smtp_pass'])
except Exception as error:
  print(f"SMTP: Failed to connect to server. {error}", file=sys.stderr)
  sys.exit(1)
finally:
  if smtp_server: smtp_server.quit()

# [search queries list]
# init queries list to fill from config file
queries=[]
# load the session search queries and corresponding args from the config list file
with open(config['file_queries'], 'r', encoding='utf-8') as file:
  for line in file:
    line=line.strip() # cleanup
    # ignore empty lines or comments
    if not line or line.startswith('#'): continue
    query_data={} # empty
    # capture everything before the first switch as search query
    pre_vars=re.split(r'(--\w+)', line, maxsplit=1)
    if len(pre_vars) > 1:
      query_data['search_query']=pre_vars[0].strip()
    # find --email and --scope settings
    email_match=re.search(r'--email=([^\s]+)', line)
    scope_match=re.search(r'--scope=([^\s]+)', line)
    # email is compulsory so if it's not there, ignore the line
    # no where to send the alert to
    if email_match:
      query_data['email']=email_match.group(1)
      if scope_match:
        query_data['scope']=scope_match.group(1)
      # build out the line to the dictionary
      queries.append(query_data)
    else:
      print(f"search.list: No alert e-mail address specified for '{line}', ignoring.")

if not queries:
  print("search.list: Nothing to do.")
  exit()



### FUNCTIONS ###

# randomise a wait time from 1 to 5 seconds by default
# also accept args to mod these
def random_wait(min_sec=1, max_sec=5):
  sleep(random.uniform(min_sec, max_sec))


def click_search_scope(text):
  spans=browser.find_elements(By.XPATH, f"//span[text()='{text}']")
  for span in spans:
    if span.is_displayed():
      span.click()
      return True
  return False


def send_alert(subject, html_content, to):
  # create the e-mail message
  # mime multipart to attach html contents
  message=MIMEMultipart()
  message['From']=config.get('pddgnimi_smtp_user')
  message['To']=to
  message['Subject']=subject
  # attach as html
  message.attach(MIMEText(html_content, 'html'))
  try:
    smtp_server=smtplib.SMTP_SSL(config['pddgnimi_smtp_host'], config['pddgnimi_smtp_port'])
    smtp_server.login(config['pddgnimi_smtp_user'], config['pddgnimi_smtp_pass'])
    smtp_server.send_message(message)
    return True
  except Exception as error:
    print(f"SMTP: {error}")
    return False
  finally:
    if smtp_server: smtp_server.quit()



### RUNTIME ###
if __name__ == "__main__":
  try:
    browser=webdriver.Firefox(service=browser_service, options=browser_options)
    for query in queries:
      search_query=query.get("search_query")
      alert_email=query.get("email")
      # if search scope is not set in search.list, default to nothing ## important ##
      # this will mean selenium won't click on the date drop down later
      # defaults to 'any time' without hardcoding
      scope=query.get("scope", None)
      random_wait()

      # go to html version of duckduckgo.com for consistent barebones search layout and no js
      browser.get("https://start.duckduckgo.com")
      random_wait()

      search_box=browser.find_element(By.ID, "searchbox_input")
      # key in ddg news bang (https://duckduckgo.com/bangs)
      search_box.send_keys('!ddgn ', search_query)
      random_wait()
      search_box.send_keys(Keys.RETURN)
      random_wait()

      # change the scope of search times, if set
      # defaults to 'any' so don't do anything unless scope is set
      match scope:
        case "day":
          click_search_scope('Any time')
          random_wait()
          click_search_scope('Past day')
          random_wait()
        case "week":
          click_search_scope('Any time')
          random_wait()
          click_search_scope('Past week')
          random_wait()
        case "month":
          click_search_scope('Any time')
          random_wait()
          click_search_scope('Past month')
          random_wait()

      # test if no results returned first
      try:
        no_results=browser.find_element(By.XPATH, "//span[contains(text(), 'No news articles found')]")
        if no_results.is_displayed():
          print(f"Search results: No news articles found for '{search_query}'.")
          continue # no results, so skip on to next query
      except element_not_found: pass # not an error, do nothing
      random_wait()

      # results container is <div id="react-layout"> so find that
      react_layout=browser.find_element(By.XPATH, '//div[@id="react-layout"]')
      # search results in <ol>
      # locate that list inside <section> that is a child of any <div> within the <article> inside <div id="react-layout">
      search_results_list=react_layout.find_element(By.XPATH, './/ancestor::article//div/section/ol')
      search_results=search_results_list.get_attribute('innerHTML')

      if search_results:
        # apply basic styling to the result from template
        with open(config['file_css_template'], 'r') as file:
          css=file.read()
        
        # set base domain for images, prepend the css template, add the search results and prettify html
        template_wrapping=[] # init
        template_wrapping.append('<base href="https://duckduckgo.com/">') # to make all external relative assets work
        template_wrapping.append('<style>') # open tag
        template_wrapping.append(css) # bump in css loaded from style template
        template_wrapping.append('</style>')
        template_wrapping.append(search_results)
        # overwrite list with it flattened
        template_wrapping=str().join(template_wrapping)

        # parse and prettify the result
        prettify_results=BeautifulSoup(template_wrapping, features="html5lib").prettify()
        with open(output_html, 'w', encoding='utf-8') as file:
          file.write(prettify_results)

        sent_alert=send_alert(f"pddgnimi: {search_query}", prettify_results, alert_email)
        if sent_alert:
          print(f"SMTP: Alert for '{search_query}' sent to {alert_email} successfully.")
        else:
          print(f"SMTP: Alert for '{search_query}' FAILED to send to {alert_email}.")

      random_wait()

  except Exception as error:
    print(f"Search results: Something went wrong getting results from DuckDuckGo.\n{error}")
    success=False
    traceback.print_exc()

  finally:
    if browser: browser.quit()
