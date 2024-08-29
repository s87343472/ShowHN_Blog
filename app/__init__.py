from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .utils import update_show_hn_posts
import pytz

def create_app():
    app = Flask(__name__)

    from .routes import main
    app.register_blueprint(main)

    scheduler = BackgroundScheduler()
    scheduler.add_job(update_show_hn_posts, 'interval', hours=24, timezone=pytz.UTC)
    scheduler.start()

    return app
