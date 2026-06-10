from datetime import datetime
from models.db import db

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    genre = db.Column(db.String(100), nullable=False, index=True)
    language = db.Column(db.String(50), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    release_date = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, nullable=True)
    poster_url = db.Column(db.String(255), nullable=True)
    trailer_url = db.Column(db.String(255), nullable=True)
    is_upcoming = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    shows = db.relationship('Show', backref='movie', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie {self.title}>"
