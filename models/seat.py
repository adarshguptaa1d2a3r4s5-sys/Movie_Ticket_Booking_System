from datetime import datetime
from models.db import db

class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id', ondelete='CASCADE'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.String(20), nullable=False, default='Regular')  # Regular, Premium, Recliner
    price = db.Column(db.Float, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Seat locking mechanism fields
    locked_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    def is_currently_locked(self):
        """Returns True if the seat is currently locked by a user and the lock has not expired."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
        
    def __repr__(self):
        return f"<Seat SeatNum:{self.seat_number} ShowID:{self.show_id} Booked:{self.is_booked}>"
