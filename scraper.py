import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options

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

def GetHtmlSource():
    # Call url to get html data
    url = 'https://www.mountaineers.org/activities/activities#c4=Climbing&b_start=0&c15=For+Beginners+(Getting+Started+Series)&c15=Easy'

    # Generate headless chrome browser to get html data, then quit
    chrome_options = Options()  
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome("/Users/albertborges/Downloads/chromedriver", chrome_options=chrome_options)
    driver.get(url)
    html = driver.page_source.encode('utf-8').strip()
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

def FNewActivitiesFound(acitivityset, activities):
    newactivities = set()

    for activity in activities:
        if activity not in acitivityset:
            newactivities.add(activity)

    return newactivities


def RefreshActivitySetWithActivityArray(activityset, activities):
    activityset.clear()

    for activity in activities:
        activityset.add(activity)

def SendMailForAcitivities(activities, newactivities, username, password):
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

        server.sendmail(gmail_user, gmail_user, msg.as_string())
        server.close()
    except:  
        print 'Something went wrong...'

# Code execution starts here

username = raw_input('Enter the email to receive notifications:')

password = getpass.getpass('Enter your password for that email:')

delay = raw_input('Enter the delay between pings in seconds:')

activityset = set()

print("Acquiring html data from mountaineers.org...")
html = GetHtmlSource()

print("Parsing html data...")
activities = ParseHtmlAndGenerateActivityTuples(html)

print("There were " + str(len(activities)) + " results found from parsing!")

newactivities = FNewActivitiesFound(activityset, activities)

print("There were " + str(len(newactivities)) + " NEW results found!")

if len(newactivities) > 0:
    RefreshActivitySetWithActivityArray(activityset, activities)

    print("Sending email to user to alert of new activities!")
    SendMailForAcitivities(activities, newactivities, username, password)

time.sleep(delay)

