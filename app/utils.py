import requests
import logging
from datetime import datetime, timedelta  # 修改这行，添加 timedelta
import pytz
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from flask import current_app, url_for
from requests.exceptions import RequestException
import time
import feedgenerator

# 初始化日志
logging.basicConfig(level=logging.INFO)

# 确保数据和截图存储路径存在
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
data_file = os.path.join(data_dir, "show_hn_posts.json")

def load_local_data():
    try:
        with open(os.path.join(data_dir, "show_hn_posts.json"), "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and 'posts' in data:
            return data['posts']
        elif isinstance(data, list):
            return data
        else:
            current_app.logger.error("Invalid data format in show_hn_posts.json")
            return []
    except Exception as e:
        current_app.logger.error(f"Error loading local data: {str(e)}")
        return []

def get_show_hn_posts():
    current_app.logger.info("Starting to fetch Show HN posts.")
    show_hn_posts = []
    
    try:
        new_stories_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
        new_stories = requests.get(new_stories_url).json()

        utc = pytz.UTC
        for story_id in new_stories[:30]:  # 限制处理的帖子数量
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = requests.get(story_url).json()

            if story and "show hn" in story.get("title", "").lower():
                post_time = datetime.fromtimestamp(story.get("time", 0), tz=utc)
                show_hn_posts.append({
                    "id": str(story['id']),
                    "title": story.get("title"),
                    "url": story.get("url", ""),
                    "description": story.get("text", ""),
                    "votes": story.get("score", 0),
                    "poster": story.get("by"),
                    "time": post_time.strftime("%Y-%m-%d %I:%M %p %Z"),
                    "date": post_time.strftime("%Y-%m-%d"),
                    "screenshot": capture_screenshot(story.get("url", "")),
                    "website_info": get_website_info(story.get("url", "")),
                })
    except RequestException as e:
        current_app.logger.error(f"Error fetching stories: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error during post fetching: {str(e)}")
    
    current_app.logger.info(f"Fetched {len(show_hn_posts)} Show HN posts.")
    return show_hn_posts

def update_show_hn_posts():
    try:
        posts = get_show_hn_posts()
        if not posts:
            current_app.logger.warning("No posts fetched. Using sample data.")
            posts = [
                {
                    "id": "sample1",
                    "title": "Sample Show HN Post",
                    "url": "https://example.com",
                    "description": "This is a sample post.",
                    "votes": 10,
                    "poster": "SampleUser",
                    "time": datetime.now(pytz.UTC).strftime("%Y-%m-%d %I:%M %p %Z"),
                    "date": datetime.now(pytz.UTC).strftime("%Y-%m-%d"),
                    "screenshot": None,
                    "website_info": "Sample website information",
                }
            ]
        
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "show_hn_posts.json"), "w") as f:
            json.dump({"posts": posts, "last_updated": datetime.now().isoformat()}, f)
        current_app.logger.info("Show HN posts updated and saved to file.")
    except Exception as e:
        current_app.logger.error(f"Error updating Show HN posts: {str(e)}")

def capture_screenshot(url):
    if not url:
        return None

    screenshot_dir = os.path.join(data_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    filename = f"{hash(url)}.png"
    filepath = os.path.join('screenshots', filename)
    full_path = os.path.join(data_dir, filepath)
    
    if os.path.exists(full_path):
        return filepath

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        driver.set_window_size(1280, 1024)
        driver.save_screenshot(full_path)
        return filepath
    except Exception as e:
        current_app.logger.error(f"Error capturing screenshot for {url}: {str(e)}")
        return None
    finally:
        driver.quit()

def get_website_info(url):
    if not url:
        return "无可用信息"

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试获取网站描述
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            return description['content']
        
        # 如果没有描述，尝试获取第一段文字
        first_paragraph = soup.find('p')
        if first_paragraph:
            return first_paragraph.text.strip()[:200] + "..."
        
        return "无可用信息"
    except Exception as e:
        current_app.logger.error(f"Error fetching website info for {url}: {str(e)}")
        return "法获取网站信息"

def generate_rss_feed():
    feed = Rss201rev2Feed(
        title="Daily Show HN",
        link="http://yourdomain.com",
        description="Daily summary of Show HN posts",
        language="en",
    )

    data = load_local_data()
    for post in data:
        feed.add_item(
            title=post['title'],
            link=post['url'],
            description=post.get('description', ''),
            pubdate=datetime.strptime(post['date'], "%Y-%m-%d"),
            unique_id=post['url']
        )

    return feed.writeString('utf-8')
