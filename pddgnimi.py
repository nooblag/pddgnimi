#!/usr/bin/python3

import elemental # wrapper for selenium
import traceback # to trace errors
import smtplib, ssl # for emails
import sys # for getting vars from commandline
import html5lib # for handling HTML5
import htmlmin # for minifying html
import re # for find/replace and regex to verify email address format
from bs4 import BeautifulSoup # for prettifying html
from time import sleep # use to slow things down even more
from email.mime.multipart import MIMEMultipart # for html emails
from email.mime.text import MIMEText # for html emails
from emailSettings import mailserverHost, mailserverPort, mailserverUser, mailserverPass # get variables to work with mailserver



### SETUP ###
# search query
if len(sys.argv) > 1:
  searchQuery = sys.argv[1] # first arg passed to this script
else:
  print('No search query.')
  print('Please enter search query as an argument.')
  print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
  exit()

# email address to send alerts to
if len(sys.argv) > 2:
  emailto = sys.argv[2] # second arg passed to this script
  # set up a check to see if email address could be possibly valid
  regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  # now pass regex to fullmatch() method to check
  if not (re.fullmatch(regex, emailto)):
      # print invalid email address in bold and notify
      print('\033[1m' + emailto + '\033[0m appears to be invalid?')
      print('Please enter a valid email address as an argument with your search query.')
      print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
      exit()
else:
  print('No email address to send alert to.')
  print('Please enter an email address as an argument with your search query.')
  print('  e.g. python3 ' + sys.argv[0] + ' "Search Query Here" emailaddress@somewhere.com')
  exit()
    
# 1 second wait time
moment = 1



### SCRAPING ###
# if we have a query
if searchQuery:
  # something to work with
  try: 
    # open browser window
    browser = elemental.Browser()
    
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

    # narrow search to be within the last day
    sleep(moment)
    browser.get_element(id="vertical_wrapper").get_element(css="div.dropdown--date", wait=moment).click()
    sleep(moment)
    browser.get_element(text="Past day", wait=moment).click()

    # get the column with results only
    sleep(moment+2) # go mega slow here
    searchResults = browser.get_element(css="div.results--main div.results.js-vertical-results", wait=moment).html



    ### DUMP TO FILE ###
    # prepare to write results to a file

    """
    # get any page CSS link references to use for styling the file save
    css = browser.get_elements(type="text/css")

    if css:
      # got something to work with
      # ensure build string is empty
      css_lines = ''
      # now grab each element captured in css and extract its HTML content
      for element in css:
        css_lines += element.html
      # set duckduckgo as a base URL for image and css assets and add search results
      result = '<base href="https://duckduckgo.com/">' + css_lines + searchResults
    else:
      # no css found but set duckduckgo as a base URL for images and add search results
      result = '<base href="https://duckduckgo.com/">' + searchResults
    """
    
    # minify filter what we have so far in order to get things consistent for find/replace below
    result = htmlmin.minify(searchResults)
    
    # remove junk span tags and text from throughout the search results
    find = "<span class=result__check__tt>Your browser indicates if you've visited this link</span>"
    result = re.sub(find, '', result)
    
    # apply basic styling to the result from template
    # get the template
    style = open("style.css", "r")
    css = style.read()
    style.close()
    # set base domain for images, prepend the css template, and add the search results
    result = '<base href="https://duckduckgo.com/">' + '<style>'+css+'</style>' + result

    # parse and prettify the result
    soup = BeautifulSoup(result,features="html5lib").prettify()
    ##soup = BeautifulSoup(result,features="html.parser").prettify()

    # now actually write
    file = open("output.html", "w")
    file.write(soup)
    file.close()
    

    ### SEND EMAIL ###
    # set up a html email
    message = MIMEMultipart("alternative")
    message["Subject"] = "pddgnimi: " + searchQuery
    message["From"] = mailserverUser
    message["To"] = emailto
    # turn the soup output from above into html MIMEText object
    emailbody = MIMEText(soup, "html")
    # add the MIME part to the message
    message.attach(emailbody)
    # open secure connection with server and send email
    with smtplib.SMTP_SSL(mailserverHost, mailserverPort, context=ssl.create_default_context()) as mailserver:
      mailserver.login(mailserverUser, mailserverPass)
      mailserver.sendmail(mailserverUser, emailto, message.as_string())


  except Exception as errorMessage:
    print('Something went wrong')
    # show the error
    print(errorMessage)
    # uncomment below to trace the error
    traceback.print_exc()

  finally:
    ### CLEAN UP ###
    if browser:
      # close browser
      browser.quit()
    # goodbye!
    exit()
     
