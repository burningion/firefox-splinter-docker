from flask import Flask
from ddtrace import tracer, patch
patch(sqlalchemy=True,psycopg=True)
from models import Video, db


# configure the tracer so that it reaches the Datadog Agent
# available in another container
tracer.configure(hostname='agent')

import os

DB_USERNAME = os.environ['POSTGRES_USER']
DB_PASSWORD = os.environ['POSTGRES_PASSWORD']


def create_app():
    """Create a Flask application"""
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    return app
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + os.environ['POSTGRES_SERVICE_HOST'] + '/' + DB_USERNAME
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    except:
        print("No POSTGRES_USER or POSTGRES_PASSWORD set for connection.")
        exit()

    db.init_app(app)
    initialize_database(app, db)
    return app


def initialize_database(app, db):
    """Drop and restore database in a consistent state"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
