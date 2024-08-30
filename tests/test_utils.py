import pytest
from app.utils import get_show_hn_posts, update_show_hn_posts
from unittest.mock import patch, MagicMock
import json
import os

@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_get_show_hn_posts(app):
    with app.app_context():
        with patch('app.utils.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = [12345, 67890]
            mock_get.return_value = mock_response

            with patch('app.utils.requests.get') as mock_get_item:
                mock_item_response = MagicMock()
                mock_item_response.json.return_value = {
                    "id": 12345,
                    "title": "Show HN: Test Post",
                    "url": "https://example.com",
                    "text": "This is a test post",
                    "score": 10,
                    "by": "testuser",
                    "time": 1625097600
                }
                mock_get_item.return_value = mock_item_response

                posts = get_show_hn_posts()

    assert len(posts) == 1
    assert posts[0]['title'] == "Show HN: Test Post"
    assert posts[0]['url'] == "https://example.com"

def test_update_show_hn_posts(app, tmpdir):
    with app.app_context():
        with patch('app.utils.get_show_hn_posts') as mock_get_posts:
            mock_get_posts.return_value = [{
                "id": "12345",
                "title": "Test Post",
                "url": "https://example.com",
                "description": "This is a test post",
                "votes": 10,
                "poster": "testuser",
                "time": "2023-06-30 12:00 PM"
            }]

            with patch('app.utils.data_dir', new=str(tmpdir)):
                update_show_hn_posts()

                assert os.path.exists(os.path.join(str(tmpdir), "show_hn_posts.json"))
                with open(os.path.join(str(tmpdir), "show_hn_posts.json"), "r") as f:
                    saved_posts = json.load(f)
                
                assert len(saved_posts) == 1
                assert saved_posts[0]['title'] == "Test Post"
