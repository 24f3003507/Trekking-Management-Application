#Data models

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

#First entity
class Users(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    role=db.Column(db.Integer,default=1) 
    username=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)
    email=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    full_name=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.String,nullable=False)

    
    booking=db.relationship("Booking",cascade="all,delete",backref="users",lazy=True) #User can access all of his bookings

    
#Entity2 Trek
class Trek(db.Model):
    __tablename__="trek"
    id = db.Column(db.Integer,primary_key=True)
    trek_name = db.Column(db.String,nullable=False)
    location = db.Column(db.String,nullable=False)
    difficulty = db.Column(db.String,nullable=False)
    duration_days = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profile.id"),nullable=True)
    status = db.Column(db.String,default="Available")
    start_date = db.Column(db.Date,nullable=False)
    end_date = db.Column(db.Date,nullable=False)
    #bookings=db.relationship("Booking",cascade="all,delete",backref="trek",lazy=True) #Trek can access all of its bookings
    

#Entity3 staff profile table
class Staff_profile(db.Model):
    __tablename__="staff_profile"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"),nullable=False)
    phone=db.Column(db.String,nullable=False)
    joined_at=db.Column(db.Date,nullable=False)
    experience_years=db.Column(db.Integer,nullable=False)
    trek=db.relationship("Trek",cascade="all,delete",backref="staff_profile",lazy=True) #Staff profile can access its treks



#Entity4 Booking table
class Booking(db.Model):
    __tablename__="booking"
    id=db.Column(db.Integer,primary_key=True)
    booking_status=db.Column(db.String,default="Pending")
    booking_date=db.Column(db.Date,nullable=False)
    payment_status=db.Column(db.String,default="Pending")
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"),nullable=False)
    trek_id=db.Column(db.Integer, db.ForeignKey("trek.id"),nullable=False)