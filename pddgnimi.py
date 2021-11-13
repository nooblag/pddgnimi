#!/usr/bin/python3

import elemental # wrapper for selenium
from bs4 import BeautifulSoup # for prettifying html
from time import sleep # use to slow things down even more
"""
import smtplib, ssl # for emails
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
"""


### SETUP ###
# 1 second wait time
moment = 1
# search query
searchQuery = "protest"
# email
mailserverHost = 'mail.riseup.net'
mailserverPort = 465
mailserverUser = ''
#mailserverPass = input("Type your password and press enter: ")
mailserverPass = ''
# address to send alerts to
emailto = ''



### SCRAPING ###
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

  # parse and prettify the result
  soup = BeautifulSoup(result,features="html5lib").prettify()

  # now actually write
  file = open("output.html", "w")
  file.write(soup)
  file.close()


  """
  ### SEND EMAIL ###
  message = MIMEMultipart("alternative")
  message["Subject"] = "test"
  message["From"] = mailserverUser
  message["To"] = emailto
  # turn the soup output from above into plain/html MIMEText object
  emailbody = MIMEText(soup, "html")
  # add the MIME part to the message
  message.attach(emailbody)
  # open secure connection with server and send email
  with smtplib.SMTP_SSL(mailserverHost, mailserverPort, context=ssl.create_default_context()) as mailserver:
    mailserver.login(mailserverUser, mailserverPass)
    mailserver.sendmail(mailserverUser, emailto, message.as_string())
  """

except: 
  print('Something went wrong')

finally:
  ### CLEAN UP ###
  if browser:
    # close browser
    browser.quit()
  # goodbye!
  exit()