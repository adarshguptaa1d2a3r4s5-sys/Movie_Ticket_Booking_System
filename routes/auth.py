from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from models.db import db
from models.user import User
from models.booking import Booking

auth_bp = Blueprint('auth', __name__)

# --- WTForms for Authentication ---
class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email address is already registered.')

# --- Routes ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('movies.home'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Account created successfully! Welcome to Adarsh Cinemas.', 'success')
        return redirect(url_for('movies.home'))
        
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('movies.home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('movies.home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
            
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('movies.home'))

@auth_bp.route('/profile')
@login_required
def profile():
    # Retrieve all bookings for current user, ordered by date
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    
    upcoming_bookings = []
    past_bookings = []
    
    current_time = datetime.utcnow()
    
    for booking in bookings:
        # Check show date and time to see if upcoming
        # Parse show date and show time
        show_datetime = datetime.combine(booking.show.show_date, booking.show.show_time)
        if show_datetime >= current_time and booking.payment_status == 'Confirmed':
            upcoming_bookings.append(booking)
        else:
            past_bookings.append(booking)
            
    return render_template(
        'profile.html', 
        upcoming_bookings=upcoming_bookings, 
        past_bookings=past_bookings
    )
