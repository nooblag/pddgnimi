#!/usr/bin/python3


### REQUISITES ###

try:
  import sys # for getting vars from commandline
  import os # for working with files
  import stat # for file permissions
  import pathlib # for getting working directory
  import configparser # to work with settings
  import getpass # handling password user input
  import base64 # for some obfuscation
  import traceback # to trace errors
  import smtplib # for SMTP connection
  import ssl # for TLS over SMTP
  import html5lib # for handling HTML5
  import json # for converting search results into html blocks
  import datetime # to prettify timestamps
  import re # for find/replace and regex to verify e-mail address format
  import email.message # used in plain text e-mail test during setup
  import email.utils # used in plain text e-mail test during setup
  from email.mime.multipart import MIMEMultipart # for HTML e-mails
  from email.mime.text import MIMEText # for HTML e-mails
  from duckduckgo_search import DDGS
except Exception as errorMessage:
  print('Error:', errorMessage)
  print("\nBefore pddgnimi can be used, your system may need some software installed:")
  bashInstall = """
    # stop on any non-zero exit status
    set -o errexit
    # check to see if pip is absent, if so, attempt to install it
    if [ ! -x "$(command -v pip)" ]; then
      pip='python3-pip'
      # try to guess some common package managers to do the install
      # debian/ubuntu types
      if [ -x "$(command -v apt)" ]; then
        installer="sudo apt update && sudo apt install ${pip}"
        printf "%s\n\n" "${installer}"
        eval "${installer}"
      # fedora/centos types
      elif [ -x "$(command -v dnf)" ]; then
        installer="sudo dnf update && sudo dnf install ${pip}"
        printf "%s\n\n" "${installer}"
        eval "${installer}"
      # can't assume a package manager
      else
        printf "%s\n\n" "${pip}" >&2
        exit 1
      fi
    fi
    # ensure python dependencies are installed
    pip install html5lib duckduckgo_search
    printf "Software check complete.\n\n"
  """
  # run bash installer
  os.system(bashInstall)
  exit()


  


### CONFIG ###

# get full path where this script is
wd = pathlib.Path(__file__).parent.absolute()
# rewrite above to ensure trailing slash!
wd = os.path.join(wd, '')

# define config file
configFile = wd + '.settings.conf'
# set up config file structure parsing
config = configparser.ConfigParser()






### SETUP ###

# prepare to check if an argument is a properly formatted e-mail address
def email_error_notify():
  print('Please enter a valid e-mail address as an argument with your search query.')
  if len(sys.argv) > 2 and sys.argv[2] == 'day' or sys.argv[2] == 'week' or sys.argv[2] == 'month' or sys.argv[2] == 'any':
    print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" ' + scope + ' emailaddress@somewhere.com')
  else:
    print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
  exit()


# regex an email address supplied as an argument
def testemail(address):
  regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  # now pass regex to fullmatch() method to check
  if not (re.fullmatch(regex, address)):
    # print invalid e-mail address in bold and notify
    print('\033[1m' + address + '\033[0m appears to be an invalid e-mail address?')
    email_error_notify()


# make config file
def makeConfig():
  # ask user some questions to set up config file
  print("\nBefore pddgnimi can be used, you need to set up a connection to a SMTP server to send e-mail alerts.")
  print("Please enter your settings below.\n")
  
  # create a section for SMTP settings
  config['SMTP'] = {}

  # now ask user for each setting
  mailserverHost = input("SMTP Hostname (e.g. smtp.somewhere.com): ")
  mailserverPort = input("Server Port (e.g. 465 for TLS): ")
  mailserverUser = input("Username/address (e.g. authaddress@somewhere.com): ")
  mailserverPass = getpass.getpass("Account password: ")

  # test settings work before writing them to a config file
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
    print("\nThere was a problem sending e-mail with the SMTP settings provided. Are you sure all the details are correct and that the server is up?")
    print('Error:', errorMessage)
    exit()

  # test successful, now create config file
  # obfuscate the SMTP login using base85-encoded bytes (https://docs.python.org/3/library/base64.html) so at least its not in plain text!
  mailserverPassEncoded = base64.b85encode(mailserverPass.encode('utf-8'))
  # create structure of variables to build config file
  config['SMTP'] = {'host': mailserverHost, 'port': mailserverPort, 'user': mailserverUser, 'auth': mailserverPassEncoded.decode('utf-8')}
  # write the settings to configFile
  with open(configFile, 'w') as saveConfig:
    config.write(saveConfig)
  # chmod the configFile 400, so only the owner can see the contents of the file. that should also help a bit ;)
  os.chmod(configFile, stat.S_IRUSR)

  # done setting up
  print("\nConfiguration successful. You're now ready to start scraping!")
  print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com\n')
  exit()





### RUNTIME ###

# if config file exists, and is a non-empty file, try to use it
if os.path.exists(configFile) and os.path.isfile(configFile) and not os.path.getsize(configFile) == 0:

  # read config file in sections
  config.read(configFile)
  mailserverHost = config['SMTP']['host']
  mailserverPort = config['SMTP']['port']
  mailserverUser = config['SMTP']['user']
  mailserverPass = config['SMTP']['auth']
  # overwrite string to decode password obfuscation and transform the result from decoded bytes
  mailserverPass = base64.b85decode(mailserverPass).decode('utf-8')


  ### parse command line arguments ###

  # search query
  if len(sys.argv) > 1:
    searchQuery = sys.argv[1] # first argument passed to this script
  else:
    print('No search query.')
    print('Please enter search query as an argument.')
    print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
    exit()

  # query scope (i.e. get news articles from past day, week, month; or any time) OR e-mail address to send alerts to
  if len(sys.argv) > 2:
    # test this argument to see if it's day|week|month|any
    if sys.argv[2] == 'day' or sys.argv[2] == 'week' or sys.argv[2] == 'month' or sys.argv[2] == 'any':
      scope = sys.argv[2] # second argument passed to this script
      if len(sys.argv) > 3:
        emailto = sys.argv[3] # third argument passed to this script
        testemail(emailto)
      else:
        print('Search query and scope accepted, but missing an e-mail address.')
        email_error_notify()
    else:
      # no scope defined, so default it to day and expect second argument to be an e-mail address
      scope = 'day'
      if len(sys.argv) > 3:
        emailto = sys.argv[3] # third argument passed to this script
      else:
        emailto = sys.argv[2] # default to second argument passed to this script
      # now run test to see if e-mail address (second argument) is valid
      testemail(emailto)
  else:
    print('No e-mail address to send alert to.')
    email_error_notify()



  ### scraping ###

  try:
    with DDGS() as search:
      results = search.news(
        searchQuery,
        region = "au-en",
        safesearch = "off",
        timelimit = scope[0], # use first character only (i.e. 'd' 'w' 'm' etc)
        max_results = 10
      )

      # set up the containers/testers
      output = []
      output_trigger = False

      # create the page and results wrapper
      output.append('<div class="results--main">')
      output.append('<div class="results js-vertical-results">')

      for result in results:
        output_trigger = True
        # start with wrapper
        output.append('<div class="result result--news result--img result--url-above-snippet">')
        output.append('<div class="result__body">')

        if result['image']:
          output.append('<div class="result__image js-result-image-wrapper">')
          output.append('<div class="result__image__plc ddgsi ddgsi-news js-result-img-placeholder" style="display: none;"></div><img class="result__image__img js-result-image" src="' + result['image'] +'"></div>')

        # title
        output.append('<h2 class="result__title"><a class="result__a" rel="noopener" href="' + result['url'] + '">' + result['title'] + '</a></h2>')

        # start wrapper for metadata
        output.append('<div class="result__extras">')
        # show which media outlet
        output.append('<div class="result__extras__url">' + result['source'])
        # break
        output.append('<span class="result__extras__sep"> | </span>')
        # try to prettify date
        # hardcode the format for now
        ddg_timestamp = datetime.datetime.strptime(result['date'], '%Y-%m-%dT%H:%M:%S+00:00')
        now = datetime.datetime.now()
        delta = now - ddg_timestamp
        timestamp = '%d hours ago' % (delta.seconds/60/60)
        output.append('<span class="result__timestamp">' + timestamp + '</span></div>')
        output.append('</div>')

        # description
        output.append('<div class="result__snippet">' + result['body'] + '</div>')

        # finish up
        output.append('</div>')
        output.append('</div>')

      # page finished
      output.append('</div>')
      output.append('</div>')

      # apply basic styling to the result from template
      # get the template
      file = open(wd + 'style.css', 'r')
      css = file.read()
      file.close()
      # set base domain for images, prepend the css template, and add the search results
      results = '<base href="https://duckduckgo.com/">' + '<style>' + css + '</style>'.join(output)

      # now actually write
      file = open(wd + '.output.html', 'w')
      file.write(results)
      file.close()

      if output_trigger:
        ### send e-mail ###
        message = MIMEMultipart("alternative")
        message["Subject"] = "pddgnimi: " + searchQuery
        message["From"] = mailserverUser
        message["To"] = emailto
        # turn the results output from above into html MIMEText object
        emailbody = MIMEText(results, "html")
        # add the MIME part to the message
        message.attach(emailbody)
        # open TLS connection and send
        with smtplib.SMTP_SSL(mailserverHost, mailserverPort, context=ssl.create_default_context()) as mailserver:
          mailserver.ehlo()
          mailserver.login(mailserverUser, mailserverPass)
          mailserver.sendmail(mailserverUser, emailto, message.as_string())
          mailserver.quit()
      else:
        print('No results.')



  except:
    print('Something went wrong.\n')
    # show and trace the error message
    traceback.print_exc()


  finally:
    exit()






# config file or settings not found
else:
  # assume this is the first runtime.
  makeConfig()
