from flask import Blueprint, render_template, current_app, url_for, abort, make_response, send_from_directory
from .utils import load_local_data, data_dir, generate_rss_feed
from collections import defaultdict
from datetime import datetime
import html
import re
import os
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    data = load_local_data()
    posts_by_date = defaultdict(list)
    for post in data:
        date = post.get('date')
        if date:
            posts_by_date[date].append(post)
    
    sorted_dates = sorted(posts_by_date.keys(), reverse=True)
    daily_summaries = []
    for date in sorted_dates:
        posts = posts_by_date[date]
        daily_summaries.append({
            'date': date,
            'title': f"Today's Show HN",
            'description': f"Discover the latest Show HN posts from Hacker News.",
            'url': url_for('main.daily_summary', date=date)
        })
    
    return render_template('index.html', daily_summaries=daily_summaries)

@main.route('/Show-HN-<date>')
def daily_summary(date):
    try:
        data = load_local_data()
        daily_posts = [post for post in data if post.get('date') == date]
        
        current_app.logger.debug(f"Posts for {date}: {daily_posts}")
        for post in daily_posts:
            if post.get('description'):
                description = html.unescape(post['description'])
                description = re.sub(r'<p>', '\n\n', description)
                description = re.sub(r'<br>|<br/>', '\n', description)
                description = re.sub(r'<[^>]+>', '', description)
                post['description'] = description.strip()

            if post.get('github_repo'):
                post['github_repo'] = html.unescape(post['github_repo'])
            
            if post.get('screenshot'):
                post['screenshot'] = os.path.basename(post['screenshot'])
                current_app.logger.debug(f"Screenshot for post: {post['screenshot']}")

        if not daily_posts:
            current_app.logger.warning(f"No posts found for date {date}")
        
        return render_template('daily_summary.html', date=date, posts=daily_posts)
    except Exception as e:
        current_app.logger.error(f"Error loading posts for date {date}: {str(e)}")
        abort(500)

@main.route('/rss')
def rss():
    try:
        feed = generate_rss_feed()
        response = make_response(feed)
        response.headers.set('Content-Type', 'application/rss+xml')
        return response
    except Exception as e:
        current_app.logger.error(f"Error serving RSS feed: {str(e)}")
        abort(500)

@main.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    screenshots_dir = os.path.join(current_app.root_path, '..', 'data', 'screenshots')
    return send_from_directory(screenshots_dir, filename)

# 如果有其他路由，保留它们
