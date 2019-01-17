import time
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

videolist =[]
for v in vids:
    try:
        tmp = 'https://www.youtube.com' + v['href']
        videolist.append(tmp)
    except:
        continue

print("Found and downloading %i videos" % len(videolist))

for item in videolist:
    print(item)
    #YouTube(item).streams.first().download()
