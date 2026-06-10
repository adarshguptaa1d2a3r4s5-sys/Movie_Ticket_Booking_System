from datetime import datetime
import uuid
from models.db import db

# Junction table representing the Booking_Seats Table
booking_seats = db.Table('booking_seats',
    db.Column('booking_id', db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), primary_key=True),
    db.Column('seat_id', db.Integer, db.ForeignKey('seats.id', ondelete='CASCADE'), primary_key=True)
)

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id', ondelete='CASCADE'), nullable=False)
    booking_reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Confirmed, Cancelled
    
    # Relationships
    seats = db.relationship('Seat', secondary=booking_seats, backref=db.backref('bookings', lazy=True))
    
    @staticmethod
    def generate_reference():
        """Generates a unique booking reference like MOV123456"""
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"MOV{unique_id}"
        
    def __repr__(self):
        return f"<Booking {self.booking_reference} - {self.payment_status}>"
