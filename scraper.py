#!/usr/bin/python

import sys

from bs4 import BeautifulSoup
from selenium import webdriver

import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import getpass

import time

class Activity:
    def __init__(self, title, date):
        self.title = title
        self.date = date

    def __hash__(self):
        return hash(self.title)

    def __str__(self):
        return self.title

def GetHtmlSource():
    # Call url to get html data
    url = 'https://www.mountaineers.org/activities/activities#c4=Climbing&b_start=0&c15=For+Beginners+(Getting+Started+Series)&c15=Easy'

    # Generate headless chrome browser to get html data, then quit
    chrome_options = Options()  
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome("/home/ubuntu/mountainerswebscraper/linux/chromedriver", chrome_options=chrome_options)
    
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-center"))
        )
        html = driver.page_source.encode('utf-8').strip()
    
    except:
        html = None

    driver.quit()

    return html

def ParseHtmlAndGenerateActivityTuples(html):
    # Utilize beautiful soup to parse the html data
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all('div', class_='result-center')
    activities = []

    for result in results:
        # Extract title
        title = result.find_all('a')

        if len(title) > 0:
            title = title[0].get_text()
        else:
            title = None

        # Extract data
        date = result.find_all('div', class_='result-date')

        if len(date) > 0:
            date = date[0].get_text()
        else:
            date = None

        activity = Activity(title, date)
        activities.append(activity)

    return activities

def FNewActivitiesFound(activityset, activities):
    newactivities = set()

    print(newactivities)

    for activity in activities:
        if activity not in activityset:
            newactivities.add(activity)

    return newactivities


def RefreshActivitySetWithActivityArray(activityset, activities):
    activityset.clear()

    for activity in activities:
        activityset.add(activity)

    print("POINTA")
    print(activityset)

def SendMailForAcitivities(activities, newactivities, username, password, target_email):
    try:  
        gmail_user = username 
        gmail_password = password

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)

        msg = MIMEMultipart('alternative')

        msg['Subject'] = "New Mountaineering Activities Found!"

        html = """\
            <html>
            <head></head>
            <body>
            """

        for activity in activities:
            color = "black"
            if activity in newactivities:
                color = "red"

            html += "\n<p style='color: " + color + ";'>" + activity.title + " - " + activity.date + "</p>\n"
        
        html += """\
            </body>
            </html>
            """

        msg.attach(MIMEText(html, 'html'))

        server.sendmail(gmail_user, target_email, msg.as_string())
        server.close()
    except:  
        print 'Something went wrong...'

# Code execution starts here

username = raw_input('Enter the email to send notifications:')

password = getpass.getpass('Enter your password for that email:')

delay = raw_input('Enter the delay between pings in seconds:')

target_email = raw_input('Enter the email to send notifications:')

activityset = set()

while True:
    print("Acquiring html data from mountaineers.org...")
    html = GetHtmlSource()

    if html is not None:
        print("Parsing html data...")
        activities = ParseHtmlAndGenerateActivityTuples(html)

        print("There were " + str(len(activities)) + " results found from parsing!")

        print("POINTZ")
        print(activityset)
        newactivities = FNewActivitiesFound(activityset, activities)

        print("There were " + str(len(newactivities)) + " NEW results found!")

        if len(newactivities) > 0:
            RefreshActivitySetWithActivityArray(activityset, activities)

            print("POINTB")
            print(activityset)

            print("Sending email to user to alert of new activities!")
            SendMailForAcitivities(activities, newactivities, username, password, target_email)
    else:
        print("Unable to find any relevant html data for activities.")

    intdelay = int(delay)
    for i in xrange(intdelay,0,-1):
        sys.stdout.write(str(i)+' seconds remaining until next request...\n')
        sys.stdout.flush()
        time.sleep(1)
