import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models.db import db
from models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Ensure media directory exists
    os.makedirs(app.config['POSTER_UPLOAD_DIR'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.movies import movies_bp
    from routes.booking import booking_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    
    # Global context processors for templates
    @app.context_processor
    def inject_globals():
        from models.theatre import Theatre
        try:
            navbar_cities = [r[0] for r in db.session.query(Theatre.city).distinct().all()]
        except Exception:
            navbar_cities = []
        return {
            'navbar_cities': navbar_cities,
            'current_year': 2026  # Anchored to 2026 timeline
        }
        
    # Build database tables if they do not exist
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    # Run the application
    app.run(debug=True)
