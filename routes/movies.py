from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, session
from sqlalchemy import or_

from models.db import db
from models.movie import Movie
from models.theatre import Theatre
from models.show import Show
from models.booking import Booking

movies_bp = Blueprint('movies', __name__)

def get_recommendations(current_movie=None, user=None, limit=4):
    """
    Recommendation Engine:
    Suggests movies based on:
      1. User's previous booking genres (if logged in)
      2. Match with current movie's genres (if viewing details)
      3. Global popularity (high rating) as a fallback
    """
    recommended_ids = set()
    recommendations = []
    
    current_id = current_movie.id if current_movie else None
    
    # 1. Based on user's booking history
    if user and user.is_authenticated:
        # Get user's confirmed bookings
        user_bookings = Booking.query.filter_by(user_id=user.id, payment_status='Confirmed').all()
        user_genres = []
        for b in user_bookings:
            genres = [g.strip() for g in b.show.movie.genre.split(',')]
            user_genres.extend(genres)
            
        if user_genres:
            # Query movies matching these genres
            genre_filters = [Movie.genre.like(f"%{g}%") for g in set(user_genres)]
            history_movies = Movie.query.filter(or_(*genre_filters)).filter(Movie.is_upcoming == False)
            if current_id:
                history_movies = history_movies.filter(Movie.id != current_id)
                
            for m in history_movies.order_by(Movie.rating.desc()).limit(limit).all():
                if m.id not in recommended_ids:
                    recommended_ids.add(m.id)
                    recommendations.append(m)

    # 2. Based on current movie's genre
    if len(recommendations) < limit and current_movie:
        current_genres = [g.strip() for g in current_movie.genre.split(',')]
        genre_filters = [Movie.genre.like(f"%{g}%") for g in current_genres]
        similar_movies = Movie.query.filter(or_(*genre_filters)).filter(Movie.is_upcoming == False).filter(Movie.id != current_id)
        
        for m in similar_movies.order_by(Movie.rating.desc()).limit(limit - len(recommendations)).all():
            if m.id not in recommended_ids:
                recommended_ids.add(m.id)
                recommendations.append(m)

    # 3. Fallback: Highly rated running movies
    if len(recommendations) < limit:
        popular_movies = Movie.query.filter(Movie.is_upcoming == False)
        if current_id:
            popular_movies = popular_movies.filter(Movie.id != current_id)
            
        for m in popular_movies.order_by(Movie.rating.desc()).limit(limit - len(recommendations)).all():
            if m.id not in recommended_ids:
                recommended_ids.add(m.id)
                recommendations.append(m)
                
    return recommendations[:limit]

@movies_bp.route('/')
def home():
    # Keep selected city in session to remember user location preferences
    selected_city = request.args.get('city') or session.get('city') or 'All'
    if selected_city != 'All':
        session['city'] = selected_city
    elif 'city' in session and request.args.get('city') == 'All':
        session.pop('city', None)
        selected_city = 'All'
        
    search_query = request.args.get('search', '').strip()
    selected_genre = request.args.get('genre', 'All')
    selected_lang = request.args.get('language', 'All')
    
    # Query distinct metadata for filter dropdowns
    cities = [r[0] for r in db.session.query(Theatre.city).distinct().all()]
    
    # Static list of major genres and languages in database for easy filtering
    genres = ['Action', 'Sci-Fi', 'Thriller', 'Adventure', 'Drama', 'Crime', 'Animation', 'Biography', 'Fantasy']
    languages = ['English', 'Hindi', 'Telugu', 'Tamil', 'Kannada', 'Japanese', 'Korean']
    
    # Base queries
    running_query = Movie.query.filter_by(is_upcoming=False)
    upcoming_query = Movie.query.filter_by(is_upcoming=True)
    
    # Apply search filter
    if search_query:
        running_query = running_query.filter(Movie.title.like(f"%{search_query}%"))
        upcoming_query = upcoming_query.filter(Movie.title.like(f"%{search_query}%"))
        
    # Apply genre filter
    if selected_genre != 'All':
        running_query = running_query.filter(Movie.genre.like(f"%{selected_genre}%"))
        upcoming_query = upcoming_query.filter(Movie.genre.like(f"%{selected_genre}%"))
        
    # Apply language filter
    if selected_lang != 'All':
        running_query = running_query.filter(Movie.language == selected_lang)
        upcoming_query = upcoming_query.filter(Movie.language == selected_lang)
        
    # Apply city filter (requires joining Theatre through Shows)
    if selected_city != 'All':
        running_query = running_query.join(Show).join(Theatre).filter(Theatre.city == selected_city).distinct()
        # Upcoming movies might not have shows scheduled yet, so they don't filter by city
        
    running_movies = running_query.order_by(Movie.rating.desc()).all()
    upcoming_movies = upcoming_query.order_by(Movie.release_date.asc()).all()
    
    # Suggest recommendations for home page (general popularity/previous booking)
    from flask_login import current_user
    recommendations = get_recommendations(user=current_user, limit=4)
    
    return render_template(
        'home.html',
        running_movies=running_movies,
        upcoming_movies=upcoming_movies,
        cities=cities,
        genres=genres,
        languages=languages,
        selected_city=selected_city,
        selected_genre=selected_genre,
        selected_lang=selected_lang,
        search_query=search_query,
        recommendations=recommendations
    )

@movies_bp.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Get active filter parameters
    selected_city = request.args.get('city') or session.get('city') or 'Mumbai'
    selected_date_str = request.args.get('date')
    
    # Unique cities where shows are active
    cities = [r[0] for r in db.session.query(Theatre.city).join(Show).filter(Show.movie_id == movie.id).distinct().all()]
    if not cities:
        cities = ['Mumbai']  # Default fallback
        
    if selected_city not in cities and cities:
        selected_city = cities[0]
        
    # Populate next 7 days for filtering
    today = date.today()
    show_dates = [today + timedelta(days=i) for i in range(7)]
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
        
    # Query shows matching selected movie, city, and date
    shows = Show.query.join(Theatre).filter(
        Show.movie_id == movie.id,
        Theatre.city == selected_city,
        Show.show_date == selected_date
    ).order_by(Show.show_time).all()
    
    # Group shows by theatre for clean presentation
    theatre_shows = {}
    for show in shows:
        if show.theatre not in theatre_shows:
            theatre_shows[show.theatre] = []
        theatre_shows[show.theatre].append(show)
        
    # Fetch recommendation cards
    from flask_login import current_user
    recommendations = get_recommendations(current_movie=movie, user=current_user, limit=4)
    
    return render_template(
        'movie_details.html',
        movie=movie,
        cities=cities,
        selected_city=selected_city,
        show_dates=show_dates,
        selected_date=selected_date,
        theatre_shows=theatre_shows,
        recommendations=recommendations
    )
