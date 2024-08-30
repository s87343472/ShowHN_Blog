from flask import Flask
from flask_apscheduler import APScheduler
from flask_caching import Cache  # 添加这行
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .utils import load_local_data, update_show_hn_posts
import threading

cache = Cache(config={'CACHE_TYPE': 'simple'})

scheduler = APScheduler()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='../data')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    scheduler.init_app(app)
    scheduler.start()

    # 首先加载本地数据
    with app.app_context():
        posts = load_local_data()
        if not posts:
            # 如果没有本地数据，才进行更新
            threading.Thread(target=update_show_hn_posts).start()

    # 设置定期更新任务
    scheduler.add_job(id='update_show_hn_posts', func=update_show_hn_posts, trigger='interval', hours=24)

    return app
