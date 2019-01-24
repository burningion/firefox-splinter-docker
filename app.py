import time, csv, os
import subprocess

from bs4 import BeautifulSoup as bs
from pytube import YouTube

from splinter import Browser

from datadog import initialize, statsd
from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware

try:
    initialize(statsd_host=os.environ['DOGSTATSD_HOST_IP'], statsd_port=8125)
    tracer.configure(
    hostname=os.environ['DD_AGENT_SERVICE_HOST'],
    port=os.environ['DD_AGENT_SERVICE_PORT'],
)

except:
    print("No environment variables for Datadog set. App won't be instrumented.")

from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

#patch traceware
traced_app = TraceMiddleware(app, tracer, service="webscraper-app", distributed_tracing=False)

#logging stuff
import logging
import json_log_formatter
import threading

# for correlating logs and traces

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)

try:
    formatter = json_log_formatter.JSONFormatter()
    json_handler = logging.FileHandler(filename='/var/log/flask/mylog.json')
    json_handler.setFormatter(formatter)
    logger = logging.getLogger('my_json')
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)
except:
    print("File logger not configured")


@app.route('/')
def hello_world():
    statsd.increment('web.page_views')
    return """
      <!doctype html>
      <title>messages</title>
    <style>body { max-width: 500px; margin: auto; padding: 1em; background: black; color: #fff; font: 16px/1.6 menlo, monospace; }</style>
    <body>
    hello!
        <pre id="out"></pre>
        <script>
            function sse() {
                var source = new EventSource('/scraper-status');
                var out = document.getElementById('out');
                source.onmessage = function(e) {
                    // XSS in chat is fun
                    out.innerHTML =  e.data + '\\n' + out.innerHTML;
                };
            }
    sse();
    </script>
    </body>
    </html>
    """

@app.route('/create-scraper', methods=['POST'])
def create_scraper():
    params = request.get_json()
    result = subprocess.Popen(['/scraper.py',
                              str(params['pages']),
                              str(params['search_terms'])])
    return 'scraping process created'

def message_stream():
    for message in range(5):
        yield "data: %i\n\n" % message
        time.sleep(1.0)

@app.route('/update-scraper', methods=['POST'])
def update_scraper():
    params = request.get_json()
    return '{"status": "ok"}'

@app.route('/scraper-status')
def scraper_status():
    return Response(message_stream(),
                    mimetype="text/event-stream")

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5005)
