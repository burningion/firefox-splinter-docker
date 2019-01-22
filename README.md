# Headless Firefox with Splinter Docker Image

This is a headless Firefox image, with Splinter running. I'm using it to scrape YouTube for videos for an upcoming talk.

Right now (Jan 2019), YouTube and Instagram only show more results when you scroll. So this is a Docker image, allowing you to scroll through the results of a page for scraping.

This is mostly a tool for me to develop in, but if you want to see how to build and use this:

```bash
$ docker build . -t firefox-splinter:latest
$ docker run  -v $(pwd)/downloads:/downloads -it firefox-splinter:latest /bin/bash
```

With this, you'll then be in the image, where you can start manipulating things:

```bash
$ python3
Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
[GCC 8.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from splinter import Browser
>>> browser = Browser('firefox', headless=True)
>>> browser.visit('https://www.youtube.com/results?search_query=clock,creativecommons')
>>> browser.execute_script("window.scrollBy(0, window.innerHeight * 2);")
>>> browser.html
```

This opens a headless browser, does a YouTube search for "clock,creativecommons", and then scrolls twice the height of the window via Javascript, forcing the next page to load.

It then prints out the HTML of the page, allowing us to extract the URLs matching our search terms.

For more info, check out the [Splinter](https://splinter.readthedocs.io/en/latest/tutorial.html) docs.

# Running in Kubernetes

This repo is also a WIP kubernetes cluster for a talk on recreating [The Clock](https://www.youtube.com/watch?v=6cOhWtyXGXQ) by Christian Marclay using Python and Machine Learning.

For now, files are downloaded using the `hostPath` mount, to my external drive. If you want to run this in a kubernetes cluster, you'll need to edit the `scraper_service.yaml` and replace it with your local path before running:

`$ kubectl apply -f scraper_service.yaml`

From there, you should be able to send stuff and generate scraping bots:

```bash
$ curl --header "Content-Type: application/json"   --request POST   --data '{"pages": 5, "search_terms": "clock,creativecommons"}' http://10.152.183.141:5005/create-scraper
```
