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
                tube = YouTube(item['url'])
                filepath = tube.streams.first().download('/downloads')
                title = tube.title
                duration = tube.length
                if int(duration) >= 300:
                    print("Skipping %s because it's too long" % title)
                    requests.post('http://localhost:5005/update-scraper', json={'message': "Skipping %s because it's too long" % title})
                    continue

                fps = tube.streams.first().fps
                caption = tube.captions.get_by_language_code('en')
                try:
                    subtitles = caption.generate_srt_captions()
                except:
                    subtitles = ''

                video = {'url': item['url'], 'title': title, 'fps': int(fps),
                         'filename': filepath, 'duration': duration,
                         'subtitles': subtitles}
                loggermessage = {'message': u"Downloaded %s" % title.encode('utf-8')}
                requests.post('http://localhost:5005/update-scraper', json=loggermessage, headers={"Content-Type": "application/json; charset=UTF-8"})

                requests.post('http://localhost:5005/videos', json=video, headers={"Content-Type": "application/json; charset=UTF-8"})
            except Exception as e:
                print("couldn't download %s, because %s" % (item['title'].encode('utf-8'), e))
                requests.post('http://localhost:5005/update-scraper', json={'message': "couldn't download %s, because %s" % (item['title'].encode('utf-8'), e)})
except IOError:
    print("couldn't open out.csv for writing %s" % IOError)
