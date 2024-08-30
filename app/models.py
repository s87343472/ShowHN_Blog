from app import db
from datetime import datetime

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PageView {self.page}>'
