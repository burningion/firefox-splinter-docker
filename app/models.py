from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import datetime

db = SQLAlchemy()

class Inference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    has_clock = db.Column(db.Boolean())
    inference = db.Column(JSON)
    clock_frames = db.Column(db.Integer())

    video_id = db.Column(db.Integer(), db.ForeignKey('video.id'))
    video = db.relationship("Video", back_populates="video")

    def __init__(self, has_clock, inference, clock_frames):
        self.has_clock = has_clock
        self.inference = inference
        self.clock_frames = clock_frames

    def serialize(self):
        return {
            'id': self.id,
            'has_clock': self.has_clock,
            'clock_frames': self.clock_frames
        }


class Video(db.Model):
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
