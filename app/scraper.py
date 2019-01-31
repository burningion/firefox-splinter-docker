#!/usr/bin/python3
import time
import csv
import argparse

from bs4 import BeautifulSoup as bs
from pytube import YouTube

from splinter import Browser

import requests

parser = argparse.ArgumentParser(description='YouTube Video Scraper')
parser.add_argument('pages', type=int, help='Number of page results to scroll', default=5)
parser.add_argument('terms', type=str, help='Search terms to search for', default="clock,creativecommons")
parser.add_argument('uid', type=str, help='UID of Scraper generated', default='000')

args = parser.parse_args()

message = "Opening browser..."
requests.post('http://localhost:5005/update-scraper', json={'message': message})


browser = Browser('firefox', headless=True)
browser.visit('https://www.youtube.com/results?search_query=%s' % args.terms)



time.sleep(2)
for i in range(args.pages):
    message ="scrolling %i..." % (i + 1)
    requests.post('http://localhost:5005/update-scraper', json={'message': message})
    time.sleep(1.5)

    browser.execute_script("window.scrollBy(0, window.innerHeight * 2);")

page = browser.html.encode()
soup = bs(page, 'html.parser')
vids = soup.findAll('a', attrs={'class':'yt-simple-endpoint style-scope ytd-video-renderer'})

columns = ['id', 'url', 'title']
videolist =[]
for v in vids:
    try:
        tmp = {'id': v['href'].split('?v=')[1],
               'url': 'https://www.youtube.com' + v['href'],
               'title': v['title']}
        videolist.append(tmp)
    except:
        continue

message = "Found and downloading %i videos" % len(videolist)
requests.post('http://localhost:5005/update-scraper', json={'message': message})

try:
    with open('/downloads/out.csv', 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for item in videolist:
            writer.writerow(item)
            try:
                message = YouTube(item['url']).streams.first().download('/downloads')
                requests.post('http://localhost:5005/update-scraper', json={'message': message})
            except:
                print("couldn't download %s" % (item['title'].encode('utf-8')))
except IOError:
    print("couldn't open out.csv for writing %s" % IOError)
