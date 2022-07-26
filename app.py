from flask import Flask
from flask_cors import CORS
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

import os
import datetime
import atexit

app = Flask(__name__)
CORS(app)

base_url = 'https://dawn.com/latest-news'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

options = Options()
options.headless = True

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

@app.route("/")
def hello_world():    
    res = requests.get(base_url, headers)
    markup = res.text
    
    soup = BeautifulSoup(markup, 'html.parser')
  
    # finding the div with the id
    all = soup.find('div', {'id': 'all'})
    pakistan = soup.find('div', {'id': 'pakistan'})
    business = soup.find('div', {'id': 'business'})
    world = soup.find('div', {'id': 'world'})
    sport = soup.find('div', {'id': 'sport'})
    
    key_arr = ['all', 'pakistan', 'business', 'world', 'sport']
    arr = [all, pakistan, business, world, sport]
    
    articles_list = []
    for item in arr:
        articles_list.append(item.findAll('article'))

    data = {}
    x = 0
    for articles in articles_list:
        temp = []
        for article in articles:
            obj = {
                'title': None,
                'excerpt': None,
                # 'text': None,
                'url': None,
                'img_src': None,
                'date_time_uploaded': None
            }

            a = article.find('a', {'class': 'story__link'})
            obj['url'] = a['href']
            obj['title'] = a.text

            excerpt = article.find('div', {'class': 'story__excerpt'})
            obj['excerpt'] = excerpt.text

            img = article.find('img')
            if img is not None:
                obj['img_src'] = img['src']

            date = article.find('span', {'class': 'timestamp__calendar'}).text
            time = article.find('span', {'class': 'timestamp__time'}).text

            date = date.replace(',', '').split(' ')
            day = int(date[0])
            month = months.index(date[1])
            year = int(date[2])

            hour = int(time[: 2])
            minute = int(time[3: 5])
            if 'pm' in time:
                if hour < 12:
                    hour = hour + 12
            
            obj['date_time_uploaded'] = datetime.datetime(year, month, day, hour, minute)

            temp.append(obj)
        data[key_arr[x]] = temp
        x += 1

    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    try:
        atexit.register(lambda: driver.close())
    except:
        pass