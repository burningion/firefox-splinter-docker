from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import datetime

db = SQLAlchemy()

class Inference(db.Model):
    __tablename__ = 'inference'
    id = db.Column(db.Integer, primary_key=True)
    has_clock = db.Column(db.Boolean())
    inference = db.Column(JSON)
    clock_frames = db.Column(db.Integer())

    video_id = db.Column(db.Integer(), db.ForeignKey('video.id'))
    video = db.relationship("Video", back_populates="inference")

    def __init__(self, has_clock, inference, clock_frames):
        self.has_clock = has_clock
        self.inference = inference
        self.clock_frames = clock_frames

    def get_snippets(self, inference_type, frame_gaps_allowed):
        frame_snippets = []

        if self.has_clock == False:
            return frame_snippets

        current_frame, start_frame, last_frame = 0, 0, 0

        for i in self.inference:
            current_frame += 1
            for detection in i['detections']:
                if inference_type == detection['type']:
                    if start_frame == 0:
                        start_frame = current_frame
                        last_frame = current_frame
                    elif (current_frame - last_frame) < frame_gaps_allowed:
                        last_frame = current_frame
                    elif (current_frame - last_frame) > frame_gaps_allowed:
                        frame_snippets.append((start_frame, last_frame))
                        start_frame = current_frame
                        last_frame = current_frame
        if start_frame > 0 and len(frame_snippets) == 0:
            frame_snippets.append((start_frame, last_frame))
        if frame_snippets[-1][1] != last_frame:
            frame_snippets.append((start_frame, last_frame))

        return frame_snippets

    def get_snippets_as_timesegments(self, inference_type, frame_gaps_allowed):
        segments = self.get_snippets(inference_type, frame_gaps_allowed)
        timesegs = []
        for segment in segments:
            start_seconds = segment[0] // self.video.fps
            length_seconds = (segment[1] // self.video.fps) - (segment[0] // self.video.fps)
            if length_seconds == 0:
                continue
            timesegs.append({'start': getHrMinSec(start_seconds),
                             'length': getHrMinSec(length_seconds)})
        return timesegs

    def serialize(self):
        if self.has_clock:
            return {'id': self.id,
                    'has_clock': self.has_clock,
                    'clock_frames': self.clock_frames,
                    'video_title': self.video.title,
                    'clock_segments': self.get_snippets_as_timesegments('clock', 10),
                    'filename': self.video.filename}

        return {'id': self.id,
                'has_clock': self.has_clock,
                'clock_frames': self.clock_frames,
                'video_title': self.video.title,
                'clock_segments': [],
                'filename': self.video.filename}


def getHrMinSec(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '{:d}:{:02d}:{:02d}'.format(h, m, s)

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    title = db.Column(db.String(256))
    fps = db.Column(db.Integer)
    duration = db.Column(db.Integer())
    subtitles = db.Column(db.Text())
    filename= db.Column(db.String(512))

    yoloed = db.Column(db.Boolean())
    inference = db.relationship("Inference", uselist=False, back_populates="video")

    def __init__(self, url, title, fps, duration, subtitles, filename, yoloed=False):
        self.url = url
        self.title = title
        self.fps = int(fps)
        self.duration = int(duration)
        self.subtitles = subtitles
        self.filename = filename
        self.yoloed = yoloed

    def serialize(self):
        if len(self.subtitles) > 0:
            subs = True
        else:
            subs = False
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'fps': self.fps,
            'duration': self.duration,
            'filename': self.filename,
            'subtitles': subs,
            'yoloed': self.yoloed
        }
