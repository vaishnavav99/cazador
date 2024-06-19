from app import db
from datetime import datetime,timezone

class User(db.Model):
    user_id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)
    leaderboard = db.relationship('Leaderboard', backref='user', lazy=True)


class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(120), db.ForeignKey('user.user_id'), nullable=False)
    updatedon = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

