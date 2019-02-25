import time, os
import subprocess

from datadog import initialize, statsd
from ddtrace import tracer

from bootstrap import create_app, db
from models import Video, Inference

import requests

inferenceURL = ''
scraperURL = ''
try:
    initialize(statsd_host=os.environ['DOGSTATSD_HOST_IP'], statsd_port=8125)
    inferenceURL = 'http://' + os.environ['INFERENCEAPP_SERVICE_HOST'] + ':' + os.environ['INFERENCEAPP_SERVICE_PORT_HTTP']
    scraperURL = 'http://' + os.environ['SCRAPERAPP_SERVICE_HOST'] + ':' + os.environ['SCRAPERAPP_SERVICE_PORT']
except :
    print("Missing an inference URL. Scraper was probably started before the Inference App.")

from flask import Flask, Response, jsonify, render_template, request

# uncomment below and comment out create_app line for no db
#app = Flask(__name__)
app = create_app()
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.logger.info('inferenceURL: %s' % inferenceURL)

@app.route('/')
def hello_world():
    statsd.increment('web.page_views')
    return render_template('index.html')

@app.route('/create-scraper', methods=['POST'])
def create_scraper():
    params = request.get_json()
    result = subprocess.Popen(['ddtrace-run',
                               'scraper.py',
                               str(params['pages']),
                               str(params['search_terms']),
                               '000'])
    return 'scraping process created'

@app.route('/videos', methods=['POST', 'GET'])
def videos():
    global inferenceURL
    if request.method == 'POST':
        video = request.get_json()
        newVid = Video(**video)
        db.session.add(newVid)
        db.session.commit()
        # post to the inference API
        requests.post(inferenceURL + '/inference', json={'filename': newVid.filename, 'postback_url': scraperURL + '/video-inference'})
        return jsonify(newVid.serialize())
    # list existing videos
    vidz = Video.query.order_by(Video.id).all()
    all_videos = []
    for video in vidz:
        all_videos.append(video.serialize())
    return jsonify({"videos": all_videos})

@app.route('/video-inference', methods=['POST', 'GET'])
def video_inference():
    if request.method == 'POST':
        inference_data = request.get_json()
        matchingVideo = Video.query.filter_by(filename=inference_data['video_file']).first()
        app.logger.info('inference called back with %s which has %i frames with clocks' % (inference_data['video_file'], inference_data['clock_frames']))
        newInference = Inference(has_clock=inference_data['has_clock'],
                                 inference=inference_data['frame_data'],
                                 clock_frames=inference_data['clock_frames'])
        newInference.video = matchingVideo
        matchingVideo.yoloed = True
        db.session.add(newInference)
        db.session.add(matchingVideo)
        db.session.commit()

        return jsonify({'inference': newInference.serialize()})
    # list existing inferences
    inferz = Inference.query.order_by(Inference.id).all()
    all_inferz = []
    for infer in inferz:
        all_inferz.append(infer.serialize())
    return jsonify({"inferences": all_inferz})

totalMessages = []
lastMessage = 0

def message_stream():
    global totalMessages, lastMessage

    while True:
        if len(totalMessages) > lastMessage:
            lastMessage += 1
            yield "data: %s\n\n" % totalMessages[-1]
        time.sleep(0.5)

@app.route('/update-scraper', methods=['POST'])
def update_scraper():
    global totalMessages

    params = request.get_json()
    span = tracer.current_span()
    span.set_tags({'request_json': params})
    totalMessages.append(params['message'])
    return '{"status": "ok", "totalMessages": %s}' % str(totalMessages)

@app.route('/scraper-status')
def scraper_status():
    return Response(message_stream(),
                    mimetype="text/event-stream")
