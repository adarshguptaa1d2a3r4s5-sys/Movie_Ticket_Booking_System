import random
from datetime import datetime, date, time, timedelta
from app import create_app
from models.db import db
from models.movie import Movie
from models.theatre import Theatre
from models.show import Show
from models.seat import Seat

def update_missing_shows():
    app = create_app()
    with app.app_context():
        print("Finding movies without any scheduled shows...")
        movies = Movie.query.all()
        theatres = Theatre.query.all()
        
        if not theatres:
            print("Error: No theatres found in the database. Cannot add shows.")
            return
            
        times_pool = [time(10, 0), time(13, 30), time(17, 0), time(20, 30)]
        today = date.today()
        dates_pool = [today + timedelta(days=i) for i in range(7)]
        
        shows_created = 0
        
        for movie in movies:
            show_count = Show.query.filter_by(movie_id=movie.id).count()
            if show_count == 0:
                print(f"Adding shows for: {movie.title} (Currently has {show_count} shows)")
                
                # Create 4 random shows for this movie across the next 7 days
                for i in range(4):
                    theatre = random.choice(theatres)
                    show_date = random.choice(dates_pool)
                    show_time = random.choice(times_pool)
                    screen_num = random.randint(1, theatre.screens)
                    
                    base_price = 250.0 if show_time.hour >= 17 else 200.0
                    
                    show = Show(
                        movie_id=movie.id,
                        theatre_id=theatre.id,
                        screen_number=screen_num,
                        show_date=show_date,
                        show_time=show_time,
                        base_price=base_price
                    )
                    db.session.add(show)
                    db.session.flush()
                    
                    rows = ['A', 'B', 'C', 'D', 'E']
                    for row in rows:
                        if row in ['A', 'B']:
                            seat_type, seat_price = 'Regular', base_price
                        elif row in ['C', 'D']:
                            seat_type, seat_price = 'Premium', base_price + 150.0
                        else:
                            seat_type, seat_price = 'Recliner', base_price + 400.0
                            
                        for col in range(1, 11):
                            seat = Seat(
                                show_id=show.id,
                                seat_number=f"{row}{col}",
                                seat_type=seat_type,
                                price=seat_price,
                                is_booked=random.random() < 0.15
                            )
                            db.session.add(seat)
                    shows_created += 1

        if shows_created > 0:
            db.session.commit()
            print(f"Success! Created {shows_created} new shows and {shows_created * 50} seats.")
        else:
            print("All movies already have scheduled shows!")

if __name__ == "__main__":
    update_missing_shows()
