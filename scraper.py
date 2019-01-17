import time
import csv

from bs4 import BeautifulSoup as bs
from pytube import YouTube
import requests

from splinter import Browser

browser = Browser('firefox', headless=True)
browser.visit('https://www.youtube.com/results?search_query=clock,creativecommons')
print("Opening browser...")

time.sleep(2)
for i in range(5):
    print("scrolling %i..." % (i + 1))
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

print("Found and downloading %i videos" % len(videolist))

try:
    with open('out.csv', 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for item in videolist:
            writer.writerow(item)
except IOError:
    print("couldn't open out.csv for writing %s" % IOError)
