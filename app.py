from email import parser
from gzip import READ
from turtle import pu
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup
import lxml

import os
import datetime
import atexit

app = Flask(__name__)
CORS(app)

base_url = 'https://dawn.com/latest-news'
news_url = 'https://www.dawn.com/news/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

options = Options()
options.headless = True

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
categories = ['All', 'Pakistan', 'Business', 'World', 'Sport']

data = []

@app.route("/")
def index():    
    return redirect('/category/All')

@app.route(f'/category/<string:key>')
def page(key):
    res = requests.get(base_url, headers)
    markup = res.text
    soup = BeautifulSoup(markup, 'html.parser')
    result = soup.find('div', {'id': key.lower()})
    articles = result.findAll('article')
    global data
    data = []
    for article in articles:
        obj = {
            'title': None,
            'excerpt': None,
            'url': None,
            'img_src': None,
            'date_time_uploaded': None
        }

        a = article.find('a', {'class': 'story__link'})
        obj['url'] = a['href'].split('/')[-2] + '_' + a['href'].split('/')[-1]
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
        data.append(obj)

    return render_template('index.html', key=key, categories=categories, data=data)

@app.route('/news/<string:url>')
def article(url):
    article_url = news_url + url.split('_')[0] + '/' + url.split('_')[1]
    res = requests.get(article_url, headers)
    markup = res.text
    
    doc = lxml.etree.fromstring(markup, parser=lxml.etree.HTMLParser())
    title = doc.xpath("//a[@class='story__link  ']")[0].text
    publish_date = doc.xpath("//span[@class='timestamp--date']")[0].text
    update_about = doc.xpath("//span[@class='timestamp--time timeago']")[0]
    timestamp_title = update_about.attrib['title']
    timestamp_time = doc.xpath("//span[@class='timestamp__time']")[0].text
    date = publish_date.replace(',', '').split(' ')
    day = int(date[1])
    month = months.index(date[0][:3]) + 1
    year = int(date[2])
    in_time = datetime.datetime.strptime(timestamp_time, "%I:%M%p")
    out_time = datetime.datetime.strftime(in_time, "%H:%M")
    hour, minute = out_time.split(':')
    time = timestamp_title[timestamp_title.index('T') + 1: timestamp_title.index('+')].split(':')
    second = time[-1]
    a = datetime.datetime(year, month, day, int(hour), int(minute), int(second))
    b = datetime.datetime.now().replace(microsecond=0)
    
    elapsed_time = str(b - a).split(',')
    if len(elapsed_time) == 1:
        hours, minutes, seconds = elapsed_time[0].split(':')
        if int(hours) > 0:
            time_ago = f'{hours} hours ago'
        elif int(minutes) > 0:
            time_ago = f'{minutes} minutes ago'
        else:
            time_ago = f'{seconds} seconds ago'
        updated = f'Updated: {time_ago}'
    else:
        updated = f'Updated: {elapsed_time[0]} ago'

    article_content = lxml.etree.tostring(doc.xpath("//div[@class='story__content  overflow-hidden    text-4  sm:text-4.5        pt-1  mt-1']")[0]).decode('utf-8')

    # if '<figure' in article_content remove it and all its children
    while '<figure' in article_content:
        start = article_content.index('<figure')
        end = article_content.index('</figure>') + len('</figure>')
        article_content = article_content[:start] + article_content[end:]

    figure = doc.xpath("//figure[@class='media      media--uneven    media--fill  sm:w-full  w-full            mb-0  ']")
    try:
        figure_string = lxml.etree.tostring(figure[0]).decode('utf-8')
        # print(figure_string)
        result = lxml.etree.fromstring(figure_string, parser=lxml.etree.HTMLParser()).xpath("//img")[0]
        image = {
            'src': result.get('src'),
            'alt': result.get('alt')
        }
    except:
        image = None

    return render_template('article.html', title=title, publish_date=publish_date, timestamp_title=timestamp_title, timestamp_time=timestamp_time, update_about=updated, image=image, article_content=article_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)