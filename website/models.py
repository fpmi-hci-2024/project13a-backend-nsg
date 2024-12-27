from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    tickets = db.relationship('Ticket')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    price = db.Column(db.Integer)
    stop_of_departure_id = db.Column(db.Integer, db.ForeignKey('route_stop.id'))
    stop_of_arrival_id = db.Column(db.Integer, db.ForeignKey('route_stop.id'))

class QualityOfService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    quality_of_service_id = db.Column(db.Integer, db.ForeignKey(QualityOfService.id))
    train_stops = db.relationship('RouteStop')

class RouteStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    time_of_arrival = db.Column(db.DateTime(timezone=True))
    time_of_departure = db.Column(db.DateTime(timezone=True))
    stop_order = db.Column(db.Integer) 

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    latitude = db.Column(db.Float)  
    longitude = db.Column(db.Float) 


