from bootstrap import create_app, db
from models import Video, Inference

app = create_app()

with app.app_context():
    import IPython
    IPython.embed(using=False) # hack for color
