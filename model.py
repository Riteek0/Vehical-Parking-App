from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash



db = SQLAlchemy()

class SpotStatus:
    AVAILABLE = 'A'
    OCCUPIED = 'O'

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=True)
    reservations = db.relationship('Reservation', back_populates='user')
    role = db.Column(db.String, nullable=False, default='user')


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default=SpotStatus.AVAILABLE)
    lot = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship('Reservation', back_populates='spot', cascade="all, delete-orphan")
    
class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    prime_location_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.String, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', back_populates='lot',cascade="all, delete-orphan")     
    
class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    vehicle_number = db.Column(db.String, nullable=False)
    parking_cost = db.Column(db.Float, nullable=False)
    spot = db.relationship('ParkingSpot', back_populates='reservations')
    user = db.relationship('User', back_populates='reservations')


#initialize the database
def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    db.init_app(app)
    

# predifined admin user
def create_admin_if_not_exists():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@parking.com',
            full_name='Administrator',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()