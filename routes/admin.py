from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, DateField, TimeField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from sqlalchemy import func

from models.db import db
from models.movie import Movie
from models.theatre import Theatre
from models.show import Show
from models.seat import Seat
from models.booking import Booking, booking_seats
from models.user import User

admin_bp = Blueprint('admin', __name__)

# --- Helper Admin Authorization ---
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

# --- WTForms for CRUD ---
class MovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired(), Length(max=150)])
    genre = StringField('Genre (comma-separated)', validators=[DataRequired(), Length(max=100)])
    language = StringField('Language', validators=[DataRequired(), Length(max=50)])
    duration = IntegerField('Duration (mins)', validators=[DataRequired(), NumberRange(min=1)])
    release_date = DateField('Release Date (YYYY-MM-DD)', validators=[DataRequired()])
    rating = FloatField('Rating (0-10)', validators=[DataRequired(), NumberRange(min=0.0, max=10.0)])
    description = TextAreaField('Description', validators=[Optional()])
    poster_url = StringField('Poster URL', validators=[Optional(), Length(max=255)])
    trailer_url = StringField('Trailer YouTube Embed URL', validators=[Optional(), Length(max=255)])
    is_upcoming = BooleanField('Is Upcoming Movie')
    submit = SubmitField('Save Movie')

class TheatreForm(FlaskForm):
    name = StringField('Theatre Name', validators=[DataRequired(), Length(max=150)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Optional(), Length(max=255)])
    screens = IntegerField('Number of Screens', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save Theatre')

class ShowForm(FlaskForm):
    movie_id = SelectField('Movie', coerce=int, validators=[DataRequired()])
    theatre_id = SelectField('Theatre', coerce=int, validators=[DataRequired()])
    screen_number = IntegerField('Screen Number', validators=[DataRequired(), NumberRange(min=1)])
    show_date = DateField('Show Date (YYYY-MM-DD)', validators=[DataRequired()])
    show_time = TimeField('Show Time (HH:MM)', validators=[DataRequired()])
    base_price = FloatField('Base Price (₹)', validators=[DataRequired(), NumberRange(min=0.0)])
    submit = SubmitField('Create Show')

# --- Dashboard & Analytics Routes ---
@admin_bp.route('/admin')
@login_required
def dashboard():
    check_admin()
    
    # 1. Total Revenue (from confirmed bookings)
    total_revenue_res = db.session.query(func.sum(Booking.total_price)).filter_by(payment_status='Confirmed').scalar()
    total_revenue = total_revenue_res if total_revenue_res else 0.0
    
    # 2. Tickets Sold (Count seats booked through confirmed bookings)
    tickets_sold = db.session.query(func.count(Seat.id)).filter(
        Seat.is_booked == True
    ).scalar() or 0
    
    # 3. Popular Movies Calculation
    popular_movies = db.session.query(
        Movie.title, func.count(Seat.id).label('tickets')
    ).join(Show, Show.movie_id == Movie.id)\
     .join(Seat, Seat.show_id == Show.id)\
     .filter(Seat.is_booked == True)\
     .group_by(Movie.title)\
     .order_by(func.count(Seat.id).desc())\
     .limit(5).all()
     
    # 4. Occupancy Rate
    total_seats = db.session.query(func.count(Seat.id)).scalar() or 1
    occupancy_rate = round((tickets_sold / total_seats) * 100, 2)
    
    # Fetch lists for CRUD management lists in tabs
    movies_list = Movie.query.order_by(Movie.release_date.desc()).all()
    theatres_list = Theatre.query.order_by(Theatre.name).all()
    shows_list = Show.query.order_by(Show.show_date.desc(), Show.show_time.desc()).all()
    users_list = User.query.order_by(User.created_at.desc()).all()
    bookings_list = Booking.query.order_by(Booking.booking_date.desc()).all()
    
    # Forms for modals or editing
    movie_form = MovieForm()
    theatre_form = TheatreForm()
    show_form = ShowForm()
    
    # Populating SelectFields for Show Form
    show_form.movie_id.choices = [(m.id, f"{m.title} ({m.language})") for m in Movie.query.filter_by(is_upcoming=False).all()]
    show_form.theatre_id.choices = [(t.id, f"{t.name} ({t.city})") for t in Theatre.query.all()]
    
    return render_template(
        'admin_dashboard.html',
        total_revenue=total_revenue,
        tickets_sold=tickets_sold,
        popular_movies=popular_movies,
        occupancy_rate=occupancy_rate,
        movies=movies_list,
        theatres=theatres_list,
        shows=shows_list,
        users=users_list,
        bookings=bookings_list,
        movie_form=movie_form,
        theatre_form=theatre_form,
        show_form=show_form
    )

# --- Charts API Endpoints for Chart.js ---
@admin_bp.route('/admin/api/analytics')
@login_required
def analytics_api():
    check_admin()
    
    # Last 7 Days Date bounds
    today = date.today()
    last_week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    date_labels = [d.strftime('%b %d') for d in last_week_dates]
    
    # Revenue Trend & Daily Bookings Count
    revenue_trend = []
    daily_bookings = []
    
    for d in last_week_dates:
        # Find sum of total_price for confirmed bookings on date `d`
        # Using database date truncation
        rev = db.session.query(func.sum(Booking.total_price))\
            .filter(func.date(Booking.booking_date) == d)\
            .filter(Booking.payment_status == 'Confirmed').scalar() or 0.0
            
        cnt = db.session.query(func.count(Booking.id))\
            .filter(func.date(Booking.booking_date) == d)\
            .filter(Booking.payment_status == 'Confirmed').scalar() or 0
            
        revenue_trend.append(round(rev, 2))
        daily_bookings.append(cnt)
        
    # Top 5 Most Booked Movies
    top_movies_query = db.session.query(
        Movie.title, func.count(Seat.id).label('seats_booked')
    ).join(Show, Show.movie_id == Movie.id)\
     .join(Seat, Seat.show_id == Show.id)\
     .filter(Seat.is_booked == True)\
     .group_by(Movie.title)\
     .order_by(func.count(Seat.id).desc())\
     .limit(5).all()
     
    popular_labels = [row[0] for row in top_movies_query]
    popular_values = [row[1] for row in top_movies_query]
    
    # Fallback to keep chart looking nice if database has no sales yet
    if not popular_labels:
        popular_labels = ["No Bookings Yet"]
        popular_values = [0]
        
    return jsonify({
        'labels': date_labels,
        'revenue_trend': revenue_trend,
        'daily_bookings': daily_bookings,
        'popular_labels': popular_labels,
        'popular_values': popular_values
    })

# --- Movie CRUD ---
@admin_bp.route('/admin/movie/add', methods=['POST'])
@login_required
def add_movie():
    check_admin()
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(
            title=form.title.data,
            genre=form.genre.data,
            language=form.language.data,
            duration=form.duration.data,
            release_date=form.release_date.data,
            rating=form.rating.data,
            description=form.description.data,
            poster_url=form.poster_url.data or "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&w=400&q=80",
            trailer_url=form.trailer_url.data or "https://www.youtube.com/embed/TcMBFSGVi1c",
            is_upcoming=form.is_upcoming.data
        )
        db.session.add(movie)
        db.session.commit()
        flash(f"Movie '{movie.title}' added successfully!", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.dashboard') + "#movies-tab")

@admin_bp.route('/admin/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    check_admin()
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    
    if form.validate_on_submit():
        form.populate_obj(movie)
        db.session.commit()
        flash(f"Movie '{movie.title}' updated successfully!", 'success')
        return redirect(url_for('admin.dashboard') + "#movies-tab")
        
    return render_template('admin_edit_form.html', form=form, title=f"Edit Movie: {movie.title}", action_url=url_for('admin.edit_movie', movie_id=movie.id))

@admin_bp.route('/admin/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    check_admin()
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash(f"Movie '{movie.title}' deleted successfully.", 'success')
    return redirect(url_for('admin.dashboard') + "#movies-tab")

# --- Theatre CRUD ---
@admin_bp.route('/admin/theatre/add', methods=['POST'])
@login_required
def add_theatre():
    check_admin()
    form = TheatreForm()
    if form.validate_on_submit():
        theatre = Theatre(
            name=form.name.data,
            city=form.city.data,
            address=form.address.data,
            screens=form.screens.data
        )
        db.session.add(theatre)
        db.session.commit()
        flash(f"Theatre '{theatre.name}' added successfully!", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.dashboard') + "#theatres-tab")

@admin_bp.route('/admin/theatre/edit/<int:theatre_id>', methods=['GET', 'POST'])
@login_required
def edit_theatre(theatre_id):
    check_admin()
    theatre = Theatre.query.get_or_404(theatre_id)
    form = TheatreForm(obj=theatre)
    
    if form.validate_on_submit():
        form.populate_obj(theatre)
        db.session.commit()
        flash(f"Theatre '{theatre.name}' updated successfully!", 'success')
        return redirect(url_for('admin.dashboard') + "#theatres-tab")
        
    return render_template('admin_edit_form.html', form=form, title=f"Edit Theatre: {theatre.name}", action_url=url_for('admin.edit_theatre', theatre_id=theatre.id))

@admin_bp.route('/admin/theatre/delete/<int:theatre_id>', methods=['POST'])
@login_required
def delete_theatre(theatre_id):
    check_admin()
    theatre = Theatre.query.get_or_404(theatre_id)
    db.session.delete(theatre)
    db.session.commit()
    flash(f"Theatre '{theatre.name}' deleted successfully.", 'success')
    return redirect(url_for('admin.dashboard') + "#theatres-tab")

# --- Show CRUD ---
@admin_bp.route('/admin/show/add', methods=['POST'])
@login_required
def add_show():
    check_admin()
    form = ShowForm()
    # Populating SelectFields again to validate
    form.movie_id.choices = [(m.id, m.title) for m in Movie.query.filter_by(is_upcoming=False).all()]
    form.theatre_id.choices = [(t.id, t.name) for t in Theatre.query.all()]
    
    if form.validate_on_submit():
        show = Show(
            movie_id=form.movie_id.data,
            theatre_id=form.theatre_id.data,
            screen_number=form.screen_number.data,
            show_date=form.show_date.data,
            show_time=form.show_time.data,
            base_price=form.base_price.data
        )
        db.session.add(show)
        db.session.flush() # get show.id to create seats
        
        # Automatically generate 50 seats for this new show!
        rows = ['A', 'B', 'C', 'D', 'E']
        for row in rows:
            if row in ['A', 'B']:
                seat_type = 'Regular'
                seat_price = show.base_price
            elif row in ['C', 'D']:
                seat_type = 'Premium'
                seat_price = show.base_price + 150.0
            else:
                seat_type = 'Recliner'
                seat_price = show.base_price + 400.0
                
            for col in range(1, 11):
                seat = Seat(
                    show_id=show.id,
                    seat_number=f"{row}{col}",
                    seat_type=seat_type,
                    price=seat_price,
                    is_booked=False
                )
                db.session.add(seat)
                
        db.session.commit()
        flash("Show created and 50 seats provisioned successfully!", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.dashboard') + "#shows-tab")

@admin_bp.route('/admin/show/delete/<int:show_id>', methods=['POST'])
@login_required
def delete_show(show_id):
    check_admin()
    show = Show.query.get_or_404(show_id)
    db.session.delete(show)
    db.session.commit()
    flash("Show deleted successfully.", 'success')
    return redirect(url_for('admin.dashboard') + "#shows-tab")
