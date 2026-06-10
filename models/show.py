from models.db import db

class Show(db.Model):
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id', ondelete='CASCADE'), nullable=False)
    screen_number = db.Column(db.Integer, default=1, nullable=False)
    show_date = db.Column(db.Date, nullable=False, index=True)
    show_time = db.Column(db.Time, nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=200.0)
    
    # Relationships
    seats = db.relationship('Seat', backref='show', lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='show', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Show ShowID:{self.id} MovieID:{self.movie_id} TheatreID:{self.theatre_id} On:{self.show_date} at:{self.show_time}>"
