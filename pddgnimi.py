#!/usr/bin/python3


### REQUISITES ###

try:
  import sys # for getting vars from commandline
  import os # for working with files
  import pathlib # for getting working directory
  import configparser # to work with settings
  import getpass # handling password user input
  import elemental # wrapper for selenium
  import traceback # to trace errors
  import smtplib # for SMTP connection
  import ssl # for TLS over SMTP
  import html5lib # for handling HTML5
  import htmlmin # for minifying HTML
  import re # for find/replace and regex to verify email address format
  import email.message # used in plain text email test during setup
  import email.utils # used in plain text email test during setup
  from bs4 import BeautifulSoup # for prettifying HTML
  from time import sleep # use to slow things down even more
  from email.mime.multipart import MIMEMultipart # for HTML emails
  from email.mime.text import MIMEText # for HTML emails
except Exception as errorMessage:
  print('Error:', errorMessage)
  # suggest how to fix missing packages. yellow colour using ANSI escape codes
  print('Have you run ' + '\033[93m' + 'pip install elemental html5lib htmlmin bs4' + '\033[00m' + ' ?')
  exit()





### CONFIG ###

# get full path where this script is
wd = pathlib.Path(__file__).parent.absolute()
# rewrite above to ensure trailing slash!
wd = os.path.join(wd, '')

# define config file
config = configparser.ConfigParser()
configFile = wd + 'settings.conf'

# 1 second wait time
moment = 1





### SETUP ###

# if config file exists, and is a non-empty file, try to use it
if os.path.exists(configFile) and os.path.isfile(configFile) and not os.path.getsize(configFile) == 0:
    # read config file in sections
    config.read(configFile)
    mailserverHost = config['SMTP']['host']
    mailserverPort = config['SMTP']['port']
    mailserverUser = config['SMTP']['user']
    mailserverPass = config['SMTP']['pass']

    # check settings aren't empty
    if not mailserverHost.strip() or not mailserverPort.strip() or not mailserverUser.strip() or not mailserverPass.strip():
      print('A SMTP configuration string is empty. Please check ' + configFile)
      exit()


    ### ENVIRONMENT ###

    # prepare to check if an argument is a properly formatted email address
    def email_error_notify():
      print('Please enter a valid email address as an argument with your search query.')
      if len(sys.argv) > 2 and sys.argv[2] == 'day' or sys.argv[2] == 'week' or sys.argv[2] == 'month' or sys.argv[2] == 'any':
        print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" ' + scope + ' emailaddress@somewhere.com')
      else:
        print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
      exit()

    def testemail(address):
      regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
      # now pass regex to fullmatch() method to check
      if not (re.fullmatch(regex, address)):
        # print invalid email address in bold and notify
        print('\033[1m' + address + '\033[0m appears to be an invalid e-mail address?')
        email_error_notify()


    # search query
    if len(sys.argv) > 1:
      searchQuery = sys.argv[1] # first arg passed to this script
    else:
      print('No search query.')
      print('Please enter search query as an argument.')
      print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
      exit()


    # query scope (i.e. get news articles from past day, week, month; or any time) OR email address to send alerts to
    if len(sys.argv) > 2:
      # test this arg to see if it's day|week|month|any
      if sys.argv[2] == 'day' or sys.argv[2] == 'week' or sys.argv[2] == 'month' or sys.argv[2] == 'any':
        scope = sys.argv[2] # second arg passed to this script
        if len(sys.argv) > 3:
          emailto = sys.argv[3] # third arg passed to this script
          testemail(emailto)
        else:
          print('Search query and scope accepted, but missing an email address.')
          email_error_notify()
      else:
        # no scope defined, so default it to day and expect 2nd argument to be an email address
        scope = 'day'
        if len(sys.argv) > 3:
          emailto = sys.argv[3] # third arg passed to this script
        else:
          emailto = sys.argv[2] # default to second arg passed to this script
        # now run test to see if email address is valid
        testemail(emailto)
    else:
      print('No email address to send alert to.')
      email_error_notify()





    ### SCRAPING ###

    try: 
      # open browser window
      browser = elemental.Browser(headless=True)
      # ensure browser window viewport is consistently big
      browser.selenium_webdriver.set_window_size(1920,1080)
      
      # go to start.duckduckgo.com for consistent barebones search layout
      browser.visit("https://start.duckduckgo.com")
      
      # find the search box and type in the query using fill
      browser.get_element(id="search_form_input_homepage").fill(searchQuery)
      
      # wait mega moments before clicking anything! duckduckgo likes to go reaaaaaally slowly, otherwise we get DOM freakouts?
      sleep(moment)
      browser.get_element(id="search_button_homepage", wait=moment).click()

      # now in search results, refine our search to be news articles only
      sleep(moment)
      browser.get_element(id="duckbar_static").get_element(text="News", wait=moment).click()

      # click on the region dropdown menu and ensure it is set to australia
      sleep(moment)
      browser.get_element(id="vertical_wrapper").get_element(css="div.dropdown--region", wait=moment).click()
      sleep(moment)
      browser.get_element(text="Australia", wait=moment).click()

      # turn safe search off
      sleep(moment)
      browser.get_element(id="vertical_wrapper").get_element(css="div.dropdown--safe-search", wait=moment).click()
      sleep(moment)
      browser.get_element(text="Off", wait=moment).click()

      # narrow search to be within the specified scope
      sleep(moment)
      browser.get_element(id="vertical_wrapper").get_element(css="div.dropdown--date", wait=moment).click()
      sleep(moment)
      if scope == 'any':
        browser.get_element(text="Any time", wait=moment).click()
      elif scope == 'week':
        browser.get_element(text="Past week", wait=moment).click()
      elif scope == 'month':
        browser.get_element(text="Past month", wait=moment).click()
      else:
        browser.get_element(text="Past day", wait=moment).click()

      # now get the column with results only
      sleep(moment+2) # go mega slow here
      searchResults = browser.get_element(css="div.results--main div.results.js-vertical-results", wait=moment).html



      ### DUMP TO FILE ###
      # prepare to write results to a file
      
      # minify filter what we have so far in order to get things consistent for find/replace below
      result = htmlmin.minify(searchResults)
      
      # remove junk span tags and text from throughout the search results
      find = "<span class=result__check__tt>Your browser indicates if you've visited this link</span>"
      result = re.sub(find, '', result)
      
      # apply basic styling to the result from template
      # get the template
      style = open(wd + 'style.css', 'r')
      css = style.read()
      style.close()
      # set base domain for images, prepend the css template, and add the search results
      result = '<base href="https://duckduckgo.com/">' + '<style>'+css+'</style>' + result

      # parse and prettify the result
      soup = BeautifulSoup(result,features="html5lib").prettify()
      ##soup = BeautifulSoup(result,features="html.parser").prettify()

      # now actually write
      file = open(wd + 'output.html', 'w')
      file.write(soup)
      file.close()
      


      ### SEND EMAIL ###

      # if we have some results, send email alert
      if not 'No news articles found for' in soup:
        # set up a html email
        message = MIMEMultipart("alternative")
        message["Subject"] = "pddgnimi: " + searchQuery
        message["From"] = mailserverUser
        message["To"] = emailto
        # turn the soup output from above into html MIMEText object
        emailbody = MIMEText(soup, "html")
        # add the MIME part to the message
        message.attach(emailbody)
        # open TLS connection and send
        with smtplib.SMTP_SSL(mailserverHost, mailserverPort, context=ssl.create_default_context()) as mailserver:
          mailserver.ehlo()
          mailserver.login(mailserverUser, mailserverPass)
          mailserver.sendmail(mailserverUser, emailto, message.as_string())
          mailserver.quit()


    except:
      print('Something went wrong.\n')
      # show and trace the error message
      traceback.print_exc()


    finally:
      ### CLEAN UP ###
      if browser:
        # close browser
        browser.quit()
      # goodbye!
      exit()






# config file or settings not found
else:
  # first runtime, ask user some questions to set up config file
  print("\nBefore pddgnimi can be used, you need to set up a connection to a SMTP server to send email alerts.")
  print("Please enter your settings below.\n")
  
  # create a section for SMTP settings
  config['SMTP'] = {}

  # now ask user for each setting
  mailserverHost = input("SMTP Hostname (e.g. smtp.somewhere.com): ")
  mailserverPort = input("Server Port (e.g. 465 for TLS): ")
  mailserverUser = input("Username/address (e.g. authaddress@somewhere.com): ")
  mailserverPass = getpass.getpass("Account password: ")

  # test settings
  try:
    message = email.message.Message()
    message["Subject"] = "pddgnimi: SMTP Test"
    message["From"] = mailserverUser
    message["To"] = mailserverUser
    message.add_header('Content-Type', 'text')
    message.set_payload("This is a test message.")
    # open TLS connection and send
    with smtplib.SMTP_SSL(mailserverHost, mailserverPort, context=ssl.create_default_context()) as mailserver:
      mailserver.ehlo()
      mailserver.login(mailserverUser, mailserverPass)
      mailserver.sendmail(mailserverUser, mailserverUser, message.as_string())
      mailserver.quit()
  except Exception as errorMessage:
    print("\nThere was a problem sending email with the SMTP settings provided. Are you sure all the details are correct and that the server is up?")
    print('Error:', errorMessage)
    exit()

  # connection successful, now create structure of variables to build config file
  config['SMTP'] = {'host': mailserverHost, 'port': mailserverPort, 'user': mailserverUser, 'pass': mailserverPass}
  # write the settings to configFile
  with open(configFile, 'w') as configFile:
    config.write(configFile)

  # done setting up
  print("\nConfiguration successful. You're now ready to start scraping!")
  print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
  exit()
