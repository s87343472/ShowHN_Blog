from flask import Blueprint, render_template, abort, request, Response
import os
import json
from datetime import datetime
from .utils import data_dir, update_show_hn_posts, generate_rss_feed

main = Blueprint('main', __name__)

@main.route('/')
def index():
    try:
        with open(os.path.join(data_dir, "show_hn_posts.json"), "r") as f:
            posts = json.load(f)
    except FileNotFoundError:
        update_show_hn_posts()
        with open(os.path.join(data_dir, "show_hn_posts.json"), "r") as f:
            posts = json.load(f)

    return render_template('index.html', posts=posts, date=datetime.now().strftime("%Y-%m-%d"))

@main.route('/post/<date>')
def blog_post(date):
    try:
        with open(os.path.join(data_dir, "show_hn_posts.json"), "r") as f:
            posts = json.load(f)
    except FileNotFoundError:
        abort(404)

    return render_template('post.html', posts=posts, date=date)

@main.route('/rss')
def rss_feed():
    try:
        with open(os.path.join(data_dir, "rss_feed.xml"), "rb") as f:
            rss_content = f.read()
    except FileNotFoundError:
        abort(404)

    return Response(rss_content, mimetype='application/rss+xml')
