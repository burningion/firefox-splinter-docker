from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    title = db.Column(db.String(256))
    fps = db.Column(db.Integer)
    duration = db.Column(db.Interval(native=True))
    subtitles = db.Column(db.Text())

    def __init__(self, url, title):
        self.url = url
        self.title = title
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url
        }
