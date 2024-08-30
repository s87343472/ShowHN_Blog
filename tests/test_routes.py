import pytest
from app import create_app
from unittest.mock import patch
import json
import os

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client, tmpdir):
    test_posts = [{
        "id": "12345",
        "title": "Test Post",
        "url": "https://example.com",
        "description": "This is a test post",
        "votes": 10,
        "poster": "testuser",
        "time": "2023-06-30 12:00 PM"
    }]

    with patch('app.routes.data_dir', new=str(tmpdir)):
        os.makedirs(str(tmpdir), exist_ok=True)
        with open(os.path.join(str(tmpdir), "show_hn_posts.json"), "w") as f:
            json.dump(test_posts, f)

        response = client.get('/')
        assert response.status_code == 200
        assert b"Test Post" in response.data
        assert b"https://example.com" in response.data

def test_index_route_no_posts(client, tmpdir):
    with patch('app.routes.data_dir', new=str(tmpdir)):
        os.makedirs(str(tmpdir), exist_ok=True)
        if os.path.exists(os.path.join(str(tmpdir), "show_hn_posts.json")):
            os.remove(os.path.join(str(tmpdir), "show_hn_posts.json"))

        with patch('app.routes.update_show_hn_posts') as mock_update:
            mock_update.return_value = None
            response = client.get('/')
            assert response.status_code == 200
            assert mock_update.called

def test_rss_route(client, tmpdir):
    test_posts = [{
        "id": "12345",
        "title": "Test Post",
        "url": "https://example.com",
        "description": "This is a test post",
        "votes": 10,
        "poster": "testuser",
        "time": "2023-06-30 12:00 PM"
    }]

    with patch('app.routes.data_dir', new=str(tmpdir)):
        os.makedirs(str(tmpdir), exist_ok=True)
        with open(os.path.join(str(tmpdir), "show_hn_posts.json"), "w") as f:
            json.dump(test_posts, f)

        response = client.get('/rss')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/rss+xml'
        assert b"Test Post" in response.data
        assert b"https://example.com" in response.data
