import requests
import logging
from datetime import datetime, timedelta
import pytz
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from flask import url_for

# 初始化日志
logging.basicConfig(level=logging.INFO)

# 确保数据和截图存储路径存在
data_dir = "data"
screenshot_dir = os.path.join(data_dir, "screenshots")
os.makedirs(screenshot_dir, exist_ok=True)

def get_show_hn_posts():
    logging.info("Starting to fetch Show HN posts.")
    show_hn_posts = []
    
    # 获取过去24小时内的帖子
    end_time = int(datetime.now().timestamp())
    start_time = end_time - 24 * 60 * 60

    # 获取新的 Show HN 帖子
    new_stories_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    new_stories = requests.get(new_stories_url).json()

    for story_id in new_stories:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()

        if story and "show hn" in story.get("title", "").lower() and start_time <= story.get("time", 0) <= end_time:
            show_hn_posts.append(process_story(story))

    return show_hn_posts

def process_story(story):
    url = story.get("url", f"https://news.ycombinator.com/item?id={story['id']}")
    screenshot_path = capture_screenshot(url, story['id'])
    website_info = get_website_info(url)

    return {
        "id": story['id'],
        "title": story.get("title"),
        "url": url,
        "description": story.get("text", ""),
        "votes": story.get("score", 0),
        "screenshot": screenshot_path,
        "website_info": website_info,
        "poster": story.get("by"),
        "time": datetime.fromtimestamp(story.get("time", 0), tz=pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %I:%M %p"),
    }

def capture_screenshot(url, story_id):
    screenshot_path = os.path.join(screenshot_dir, f"{story_id}.png")
    if os.path.exists(screenshot_path):
        return screenshot_path

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.set_window_size(1280, 800)
        driver.save_screenshot(screenshot_path)
        driver.quit()
        logging.info(f"Screenshot generated for story {story_id}.")
    except Exception as e:
        logging.error(f"Error generating screenshot for {url}: {e}")
        return "/static/images/screenshot_placeholder.png"

    return screenshot_path

def get_website_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        description = soup.find('meta', attrs={'name': 'description'})
        return description['content'] if description else "No additional info available."
    except Exception as e:
        logging.error(f"Error fetching website info for {url}: {e}")
        return "No additional info available."

def update_show_hn_posts():
    posts = get_show_hn_posts()
    with open(os.path.join(data_dir, "show_hn_posts.json"), "w") as f:
        json.dump(posts, f)
    
    # 生成新的 RSS feed
    host_url = "http://yourdomain.com"  # 替换为你的实际域名
    rss_feed = generate_rss_feed(posts, host_url)
    with open(os.path.join(data_dir, "rss_feed.xml"), "wb") as f:
        f.write(rss_feed)
    
    logging.info("Show HN posts and RSS feed updated and saved to file.")

def generate_rss_feed(posts, host_url):
    fg = FeedGenerator()
    fg.title('Show HN Daily')
    fg.description('Daily summary of Show HN posts from Hacker News')
    fg.link(href=host_url)

    for post in posts:
        fe = fg.add_entry()
        fe.title(post['title'])
        fe.link(href=post['url'])
        fe.description(post['description'])
        fe.pubDate(datetime.strptime(post['time'], "%Y-%m-%d %I:%M %p"))

    return fg.rss_str(pretty=True)
