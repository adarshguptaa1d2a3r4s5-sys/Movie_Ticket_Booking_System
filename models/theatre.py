from models.db import db

class Theatre(db.Model):
    __tablename__ = 'theatres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=True)
    screens = db.Column(db.Integer, default=1, nullable=False)
    
    # Relationships
    shows = db.relationship('Show', backref='theatre', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Theatre {self.name} - {self.city}>"
