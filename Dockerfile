FROM ubuntu:latest
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update && apt-get install -y software-properties-common wget python3 python3-pip python3-dev libpq-dev
RUN add-apt-repository -y ppa:mozillateam/firefox-next
RUN apt-get update && apt-get install -y firefox \
  && rm -rf /var/lib/apt/lists/*
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz && tar zxvf geckodriver-v0.23.0-linux64.tar.gz && mv geckodriver /bin/
RUN python3 -m pip install splinter pytube beautifulsoup4 requests ipython
COPY app/requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY app/ ./
EXPOSE 5005
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
CMD ["ddtrace-run", "flask", "run", "--port=5005", "--host=0.0.0.0"]
