import random
from datetime import datetime, date, time, timedelta
from app import create_app
from models.db import db
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.show import Show
from models.seat import Seat

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database tables...")
        db.drop_all()
        db.create_all()
        
        # 1. Create Users
        print("Seeding Users...")
        admin = User(
            name="System Administrator",
            email="adarshguptaa1d2a3r4s5@gmail.com",
            phone="9876543210",
            is_admin=True
        )
        admin.set_password("adarsh123")
        
        test_user = User(
            name="John Doe",
            email="user@booking.com",
            phone="9988776655",
            is_admin=False
        )
        test_user.set_password("user123")
        
        db.session.add(admin)
        db.session.add(test_user)
        
        # 2. Create 20 Movies
        print("Seeding Movies...")
        movies_data = [
            {
                "title": "Avengers: Endgame",
                "genre": "Action, Sci-Fi",
                "language": "English",
                "duration": 181,
                "release_date": date(2019, 4, 26),
                "rating": 8.4,
                "description": "After the devastating events of Avengers: Infinity War (2018), the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos' actions and restore balance to the universe.",
                "poster_url": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/TcMBFSGVi1c",
                "is_upcoming": False
            },
            {
                "title": "Inception",
                "genre": "Sci-Fi, Action, Thriller",
                "language": "English",
                "duration": 148,
                "release_date": date(2010, 7, 16),
                "rating": 8.8,
                "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the project.",
                "poster_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/YoHD9XEInc0",
                "is_upcoming": False
            },
            {
                "title": "The Dark Knight",
                "genre": "Action, Crime, Drama",
                "language": "English",
                "duration": 152,
                "release_date": date(2008, 7, 18),
                "rating": 9.0,
                "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "poster_url": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/LDG9bisJEaI",
                "is_upcoming": False
            },
            {
                "title": "Interstellar",
                "genre": "Sci-Fi, Adventure, Drama",
                "language": "English",
                "duration": 169,
                "release_date": date(2014, 11, 7),
                "rating": 8.7,
                "description": "When Earth becomes uninhabitable, a team of explorers travels through a wormhole in space in an attempt to ensure humanity's survival.",
                "poster_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/zSWdZVtXT7E",
                "is_upcoming": False
            },
            {
                "title": "Avatar: The Way of Water",
                "genre": "Sci-Fi, Action, Adventure",
                "language": "English",
                "duration": 192,
                "release_date": date(2022, 12, 16),
                "rating": 7.6,
                "description": "Jake Sully lives with his newfound family formed on the extrasolar moon Pandora. Once a familiar threat returns to finish what was previously started, Jake must work with Neytiri and the army of the Na'vi race to protect their home.",
                "poster_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/d9MyW72ELq0",
                "is_upcoming": False
            },
            {
                "title": "Oppenheimer",
                "genre": "Drama, Biography",
                "language": "English",
                "duration": 180,
                "release_date": date(2023, 7, 21),
                "rating": 8.9,
                "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
                "poster_url": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/uYPbbksJxIg",
                "is_upcoming": False
            },
            {
                "title": "Dune: Part Two",
                "genre": "Sci-Fi, Adventure",
                "language": "English",
                "duration": 166,
                "release_date": date(2024, 3, 1),
                "rating": 8.8,
                "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                "poster_url": "https://images.unsplash.com/photo-1547483238-2cbf88bf2443?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/Way9Dexny3w",
                "is_upcoming": False
            },
            {
                "title": "Kalki 2898 AD",
                "genre": "Action, Sci-Fi",
                "language": "Telugu",
                "duration": 180,
                "release_date": date(2024, 6, 27),
                "rating": 7.8,
                "description": "A modern avatar of Vishnu, a Hindu god, who is believed to have descended to earth to protect the world from evil forces.",
                "poster_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/kQDd1AhGIHk",
                "is_upcoming": False
            },
            {
                "title": "Jawan",
                "genre": "Action, Thriller",
                "language": "Hindi",
                "duration": 168,
                "release_date": date(2023, 9, 7),
                "rating": 7.5,
                "description": "A high-octane action thriller which outlines the emotional journey of a man who is set to rectify the wrongs in the society.",
                "poster_url": "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/MWOlvJa5Nz4",
                "is_upcoming": False
            },
            {
                "title": "Sholay",
                "genre": "Action, Adventure, Comedy",
                "language": "Hindi",
                "duration": 204,
                "release_date": date(1975, 8, 15),
                "rating": 8.2,
                "description": "After his family is murdered by a notorious bandit, a former police officer hires two outlaws to capture him.",
                "poster_url": "https://images.unsplash.com/photo-1533928298208-27ff66555d8d?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/hLhNZaVnLg4",
                "is_upcoming": False
            },
            {
                "title": "Kantara",
                "genre": "Action, Drama, Thriller",
                "language": "Kannada",
                "duration": 149,
                "release_date": date(2022, 9, 30),
                "rating": 8.3,
                "description": "It involves culture of Sacred Customs and Rituals, Demigod, and Forest protection. A conflict between good and evil where local villagers stand up for their rights against greedy corporate and government entities.",
                "poster_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/8qlDFcM8X8c",
                "is_upcoming": False
            },
            {
                "title": "Leo",
                "genre": "Action, Crime, Thriller",
                "language": "Tamil",
                "duration": 164,
                "release_date": date(2023, 10, 19),
                "rating": 7.2,
                "description": "A mild-mannered cafe owner becomes a local hero, but his actions trigger ghosts from his past who are convinced he is a former syndicate hitman.",
                "poster_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/Po3jGGPKqyU",
                "is_upcoming": False
            },
            # Upcoming Movies (5 movies)
            {
                "title": "Avatar 3: Fire and Ash",
                "genre": "Sci-Fi, Action, Adventure",
                "language": "English",
                "duration": 170,
                "release_date": date(2025, 12, 19),
                "rating": 0.0,
                "description": "The upcoming third installment in James Cameron's blockbuster Avatar franchise, exploring new fire-based tribes on Pandora.",
                "poster_url": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/d9MyW72ELq0",
                "is_upcoming": True
            },
            {
                "title": "Sherlock Holmes 3",
                "genre": "Mystery, Action, Crime",
                "language": "English",
                "duration": 135,
                "release_date": date(2026, 8, 14),
                "rating": 0.0,
                "description": "Robert Downey Jr. and Jude Law return for the third installment of the stylized mystery adventure series directed by Guy Ritchie.",
                "poster_url": "https://images.unsplash.com/photo-1585647347483-22b66260dfff?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/N73oKdsq-s4",
                "is_upcoming": True
            },
            {
                "title": "Spider-Man: Beyond the Spider-Verse",
                "genre": "Animation, Action, Adventure",
                "language": "English",
                "duration": 140,
                "release_date": date(2026, 12, 18),
                "rating": 0.0,
                "description": "The grand finale to Miles Morales' dimensional travel trilogy, confronting the Spot and alternative versions of himself.",
                "poster_url": "https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/g4Hbz2jWDvQ",
                "is_upcoming": True
            },
            {
                "title": "War 2",
                "genre": "Action, Thriller",
                "language": "Hindi",
                "duration": 155,
                "release_date": date(2025, 8, 14),
                "rating": 0.0,
                "description": "The next explosive entry in the YRF Spy Universe, featuring Kabir and a deadly new antagonist facing off across global arenas.",
                "poster_url": "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/MWOlvJa5Nz4",
                "is_upcoming": True
            },
            {
                "title": "Pushpa 2: The Rule",
                "genre": "Action, Crime, Drama",
                "language": "Telugu",
                "duration": 175,
                "release_date": date(2024, 12, 5),
                "rating": 0.0,
                "description": "The clash continues between Pushpa Raj and Bhanwar Singh Shekhawat in this action-packed sequel to the 2021 blockbuster.",
                "poster_url": "https://images.unsplash.com/photo-1608889174633-8a39e24ecf2a?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/1kVPXsVq9Lo",
                "is_upcoming": True
            },
            # Remaining running movies to make 20 total
            {
                "title": "Spirited Away",
                "genre": "Animation, Fantasy, Family",
                "language": "Japanese",
                "duration": 125,
                "release_date": date(2001, 7, 20),
                "rating": 8.6,
                "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
                "poster_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/ByXuk9QqQkk",
                "is_upcoming": False
            },
            {
                "title": "Parasite",
                "genre": "Thriller, Drama, Comedy",
                "language": "Korean",
                "duration": 132,
                "release_date": date(2019, 5, 30),
                "rating": 8.5,
                "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                "poster_url": "https://images.unsplash.com/photo-1593085512500-5d55148d6f0d?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/5xH0HfJHsaY",
                "is_upcoming": False
            },
            {
                "title": "Whiplash",
                "genre": "Drama, Music",
                "language": "English",
                "duration": 107,
                "release_date": date(2014, 10, 10),
                "rating": 8.5,
                "description": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
                "poster_url": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=400&q=80",
                "trailer_url": "https://www.youtube.com/embed/7d_jQyGldEs",
                "is_upcoming": False
            }
        ]
        
        movies = []
        for item in movies_data:
            movie = Movie(**item)
            db.session.add(movie)
            movies.append(movie)
        
        # Flush to get IDs
        db.session.flush()
        
        # 3. Create 10 Theatres
        print("Seeding Theatres...")
        theatres_data = [
            {"name": "PVR Phoenix High Street", "city": "Mumbai", "address": "Phoenix Mills, Lower Parel", "screens": 4},
            {"name": "INOX Nariman Point", "city": "Mumbai", "address": "CR2 Mall, Nariman Point", "screens": 3},
            {"name": "PVR Director's Cut", "city": "Delhi", "address": "Ambience Mall, Vasant Kunj", "screens": 2},
            {"name": "Cinepolis Saket", "city": "Delhi", "address": "DLF Avenue Mall, Saket", "screens": 5},
            {"name": "PVR Forum Mall", "city": "Bangalore", "address": "Forum Mall, Koramangala", "screens": 4},
            {"name": "INOX Lido Mall", "city": "Bangalore", "address": "Lido Mall, Ulsoor", "screens": 3},
            {"name": "PVR ICON Pavilion", "city": "Pune", "address": "Pavilion Mall, SB Road", "screens": 4},
            {"name": "Cinepolis Seasons Mall", "city": "Pune", "address": "Seasons Mall, Magarpatta", "screens": 5},
            {"name": "PVR Galleria", "city": "Gurugram", "address": "Galleria Market, Phase 4", "screens": 2},
            {"name": "INOX Elante Mall", "city": "Chandigarh", "address": "Elante Mall, Phase 1", "screens": 4}
        ]
        
        theatres = []
        for item in theatres_data:
            theatre = Theatre(**item)
            db.session.add(theatre)
            theatres.append(theatre)
            
        db.session.flush()
        
        # Use ALL movies for show generation (including upcoming) so every movie is bookable
        all_movies = movies
        
        # 4. Create Shows and Seats — EVERY movie gets shows in EVERY city on EVERY date
        print("Seeding Shows and Seats (full coverage for all movies)...")
        
        # Setup showtimes
        times_pool = [
            time(10, 0),   # 10:00 AM
            time(13, 30),  # 01:30 PM
            time(17, 0),   # 05:00 PM
            time(20, 30)   # 08:30 PM
        ]
        
        # Spread shows across next 7 days
        today = date.today()
        dates_pool = [today + timedelta(days=i) for i in range(7)]
        
        # Group theatres by city for easy lookup
        city_theatres = {}
        for theatre in theatres:
            if theatre.city not in city_theatres:
                city_theatres[theatre.city] = []
            city_theatres[theatre.city].append(theatre)
        
        show_count = 0
        
        # For EVERY movie, create shows in EVERY city on EVERY date
        for movie in all_movies:
            for show_date in dates_pool:
                for city, city_theatre_list in city_theatres.items():
                    # Pick 2 random showtimes per movie per city per date
                    daily_times = random.sample(times_pool, min(2, len(times_pool)))
                    
                    for show_time in daily_times:
                        theatre = random.choice(city_theatre_list)
                        screen_num = random.randint(1, theatre.screens)
                        
                        # Evening shows cost more
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
                        db.session.flush()  # to get show.id
                        
                        # Seed 50 seats for this show (5 rows × 10 seats)
                        rows = ['A', 'B', 'C', 'D', 'E']
                        for row in rows:
                            if row in ['A', 'B']:
                                seat_type = 'Regular'
                                seat_price = base_price
                            elif row in ['C', 'D']:
                                seat_type = 'Premium'
                                seat_price = base_price + 150.0
                            else:
                                seat_type = 'Recliner'
                                seat_price = base_price + 400.0
                                
                            for col in range(1, 11):
                                seat_number = f"{row}{col}"
                                is_booked = random.random() < 0.15
                                
                                seat = Seat(
                                    show_id=show.id,
                                    seat_number=seat_number,
                                    seat_type=seat_type,
                                    price=seat_price,
                                    is_booked=is_booked
                                )
                                db.session.add(seat)
                        
                        show_count += 1
                        
            # Batch commit per movie to avoid huge transaction
            db.session.flush()
            print(f"  [OK] {movie.title}: {show_count} total shows created so far...")
                
        # Commit all transactions
        print("Saving everything to database...")
        db.session.commit()
        print("\nDatabase Seeding Successful!")
        print(f"Total Movies: {len(movies)}")
        print(f"Total Theatres: {len(theatres)}")
        print(f"Total Shows: {show_count}")
        print(f"Total Seats Created: {show_count * 50}")
        print(f"\nEvery movie now has shows in {len(city_theatres)} cities across 7 days!")
        print("Default accounts created:")
        print("  - Admin: adarshguptaa1d2a3r4s5@gmail.com / adarsh123")
        print("  - Standard User: user@booking.com / user123")

if __name__ == "__main__":
    seed_database()
