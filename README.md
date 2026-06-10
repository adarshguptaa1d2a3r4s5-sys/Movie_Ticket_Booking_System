# Advanced Movie Ticket Booking System 🍿

A highly premium, full-stack Movie Ticket Booking application built in **Python (Flask)** and **SQLAlchemy (ORM)** with a sleek, responsive, **Netflix-inspired dark theme** (`#0F172A`, `#E50914`, `#FFFFFF`). This system provides movie searching/filtering, automated recommendation cards, interactive seat maps with a **real-time 5-minute seat reservation locking mechanism**, custom QR code ticket generation, automated invoice math, and downloadable PDF tickets. It also includes an advanced **Admin Dashboard** showing dynamic analytics graphs powered by Chart.js.

---

## 🚀 Key Features

* **Authentication System**: Secure user sign-up and log-in utilizing `Flask-Login` session tracking and `Werkzeug` cryptographic password hashing.
* **Cinematic Home Page**: Movie showcases separated by "Now Showing" and "Coming Soon" with rating cards, search facilities, and multi-tier filters (by Language, Genre, and City).
* **Robust Recommendation Engine**: Algorithmic scoring that suggests active shows based on the user's booking history, current movie genres, and ratings.
* **Dynamic Seat Reservation**: Responsive seat map representing Row configurations (A-E) and columns (1-10) with automatic pricing tiers (Regular ₹200, Premium ₹350, Recliner ₹600).
* **Atomic Seat Locking**: A database-backed secure API locking picked seats for 5 minutes via a `locked_until` column, preventing double-bookings.
* **Mock Payment Gateway**: Simulated portal supporting UPI, Cards, and NetBanking with auto-unlocking on cancellation/failure.
* **PDF & QR Code Ticket Service**: Automatically compiles base64 QR codes containing JSON order payloads and generates beautiful, download-ready PDF tickets using the `ReportLab` library.
* **Interactive Admin Controls & Charts**: CRUD interfaces to manage Movies, Theatres, and Shows, plus an analytics suite compiling Revenue, Occupancy Rates, and Ticket Volumes in graphical visual widgets powered by `Chart.js`.

---

## 🛠️ Tech Stack

* **Backend**: Python 3.12, Flask, SQLAlchemy ORM, Flask-Login, Flask-WTF Forms (WTForms)
* **Database**: SQLite (Development) / PostgreSQL (Production ready)
* **Frontend**: HTML5, CSS3 (Custom Styles), Bootstrap v5.3.3, Vanilla JavaScript, AJAX (fetch)
* **Utilities**: `reportlab` (PDF generation), `qrcode` (QR base64 compiler), `Pillow`

---

## 📂 Project Structure

```
movie_ticket_system/
│
├── app.py                  # Flask Application Factory & Initialization
├── config.py               # Config parameters & Directory creations
├── seed.py                 # Core database resets and populator script
├── requirements.txt        # Production & Development dependencies
│
├── database/
│   └── movies.db           # SQLite DB file (automatically provisioned)
│
├── models/                 # Database Schema definitions
│   ├── __init__.py
│   ├── db.py               # Central SQL db object to avoid circular inputs
│   ├── user.py             # Accounts & Admin settings
│   ├── movie.py            # Synopsis, ratings, release state
│   ├── theatre.py          # Cinema names, cities, address screens count
│   ├── show.py             # Schedules, date, timings, screens, base prices
│   ├── seat.py             # Individual seat numbering, bookings, locks
│   └── booking.py          # Invoice transactions and seat mappings
│
├── routes/                 # App blueprints controllers
│   ├── __init__.py
│   ├── auth.py             # Login/Register + User profile dashboards
│   ├── movies.py           # Browsing explorer + Recommendation engine
│   ├── booking.py          # Seat picking, active locking, payment, PDF/QR
│   └── admin.py            # CRUD operations + stats REST API
│
├── static/                 # Static asset delivery
│   ├── css/
│   │   └── style.css       # Netflix dark aesthetics & seat maps styling
│   └── js/
│       ├── main.js         # Alerts and Chart.js dashboards triggers
│       └── seats.js        # Selection controls, live billing, lock AJAX, timer
│
├── templates/              # HTML layout components
│   ├── base.html           # Master navigation & footer layout
│   ├── home.html           # Spotlights carousel & lists
│   ├── movie_details.html  # YouTube trailer embeds & show timings
│   ├── seat_selection.html # Responsive grids & billing sidebars
│   ├── payment_gateway.html# Simulated banks forms
│   ├── booking_confirmation.html # QR displays & PDF downloads
│   ├── login.html / register.html # Authentications WTForms
│   ├── profile.html        # Account & ticket history timelines
│   ├── admin_dashboard.html# Charts & CRUD overlays
│   └── admin_edit_form.html# Inline updates
│
└── utils/                  # Library services
    ├── __init__.py
    ├── price_calculator.py # Tax, Convenience, and Base aggregators
    ├── qr_generator.py     # Base64 string & Image bytes compilers
    └── pdf_generator.py    # ReportLab ticket compiler
```

---

## 🛢️ Database Schema Design

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : places
    MOVIES ||--o{ SHOWS : schedules
    THEATRES ||--o{ SHOWS : hosts
    SHOWS ||--o{ SEATS : has
    SHOWS ||--o{ BOOKINGS : invoices
    BOOKINGS ||--|{ BOOKING_SEATS : contains
    SEATS ||--|{ BOOKING_SEATS : belongs
    
    USERS {
        int id PK
        string name
        string email
        string password_hash
        string phone
        boolean is_admin
        datetime created_at
    }
    
    MOVIES {
        int id PK
        string title
        string genre
        string language
        int duration
        date release_date
        float rating
        text description
        string poster_url
        string trailer_url
        boolean is_upcoming
    }
    
    THEATRES {
        int id PK
        string name
        string city
        string address
        int screens
    }
    
    SHOWS {
        int id PK
        int movie_id FK
        int theatre_id FK
        int screen_number
        date show_date
        time show_time
        float base_price
    }
    
    SEATS {
        int id PK
        int show_id FK
        string seat_number
        string seat_type
        float price
        boolean is_booked
        int locked_by_user_id FK
        datetime locked_until
    }
    
    BOOKINGS {
        int id PK
        int user_id FK
        int show_id FK
        string booking_reference
        float total_price
        datetime booking_date
        string payment_status
    }
    
    BOOKING_SEATS {
        int booking_id FK
        int seat_id FK
    }
```

---

## 💻 Local Quick Start

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your system.

### 2. Clone and Setup Environment
Navigate into the workspace folder and install the dependencies:
```bash
# Install dependencies from the requirements file
pip install -r requirements.txt
```

### 3. Reset and Seed Database
Populate your database with rich testing metrics, scheduling tables, and exactly **5,000 seat records** across 100 shows:
```bash
python seed.py
```
*This will provision testing accounts:*
* **Standard User Account**: `user@booking.com` / `user123`
* **Admin Account**: `admin@booking.com` / `admin123`

### 4. Boot Dev Server
Start the Flask local development server:
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## ☁️ Production Deployment Guide

### Option 1: Deploying on Render (Free / Hobby Tier)

Render makes it extremely simple to deploy Python/Flask services connecting to PostgreSQL.

1. **Push Code to Git**: Put your project files in a Git repository (GitHub/GitLab).
2. **Create a PostgreSQL Database on Render**:
   - Go to the Render Dashboard, click **New +**, and select **PostgreSQL**.
   - Set Name, Region, and Database Name.
   - Click **Create Database**. Once provisioned, copy the **Internal Database URL** or **External Database URL**.
3. **Create a Web Service on Render**:
   - Click **New +** and select **Web Service**.
   - Link your Git repository.
   - Set settings:
     * **Environment**: `Python 3`
     * **Build Command**: `pip install -r requirements.txt`
     * **Start Command**: `gunicorn "app:create_app()"` (Add `gunicorn` in `requirements.txt` if needed, or use a custom python command)
4. **Configure Environment Variables**:
   In the **Variables** tab on Render, add:
   * `DATABASE_URL`: *(Paste your PostgreSQL Connection URL from Step 2)*
   * `SECRET_KEY`: `your_custom_production_key_here`
   * `FLASK_ENV`: `production`
5. **Initialize database schemas**:
   Render will build and run. To run the initial seeder, you can navigate to the **Shell** tab in your Web Service dashboard on Render and trigger:
   ```bash
   python seed.py
   ```
   This resets the PostgreSQL DB and seeds the testing dataset cleanly.

---

### Option 2: Deploying on a VPS (Ubuntu / Debian Dedicated Server)

A robust production pipeline on Ubuntu using **Nginx**, **Gunicorn**, and **Systemd**.

#### 1. Server System Updates & DB Install
```bash
# Update repositories and install system packages
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx postgresql postgresql-contrib -y
```

#### 2. Configure PostgreSQL
```bash
# Log into PostgreSQL prompt
sudo -i -u postgres psql

# Create DB, user and passwords
CREATE DATABASE movies_db;
CREATE USER booking_admin WITH PASSWORD 'Antigravity_Red_Accents_99!';
GRANT ALL PRIVILEGES ON DATABASE movies_db TO booking_admin;
\q
```

#### 3. Clone Repository & Setup Virtual Environment
```bash
# Clone to /var/www
sudo mkdir -p /var/www/movie_ticket_system
sudo chown -R ubuntu:ubuntu /var/www/movie_ticket_system
git clone <your-repo-url> /var/www/movie_ticket_system

# Configure virtual environment
cd /var/www/movie_ticket_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Install production server WSGI
```

#### 4. Configure Application Environment Settings
Create a `.env` file inside `/var/www/movie_ticket_system/.env`:
```env
FLASK_ENV=production
SECRET_KEY=netflix_style_glowing_red_accents_key_prod
DATABASE_URL=postgresql://booking_admin:Antigravity_Red_Accents_99!@localhost/movies_db
```

#### 5. Setup Systemd Service
Create a Systemd configuration `/etc/systemd/system/movies.service`:
```ini
[Unit]
Description=Antigravity Movies Flask Application Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/movie_ticket_system
EnvironmentFile=/var/www/movie_ticket_system/.env
ExecStart=/var/www/movie_ticket_system/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 "app:create_app()"

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable movies
sudo systemctl start movies
# Verify it boots correctly:
sudo systemctl status movies
```

#### 6. Database Migrations / Seeding
To run database seeder on production Postgres:
```bash
cd /var/www/movie_ticket_system
source venv/bin/activate
export DATABASE_URL=postgresql://booking_admin:Antigravity_Red_Accents_99!@localhost/movies_db
python seed.py
```

#### 7. Reverse Proxy Configuration (Nginx)
Create the Nginx block configuration file `/etc/nginx/sites-available/movies`:
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/movie_ticket_system/static/;
    }
}
```
Mount and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/movies /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
*(Optional)* Add SSL support easily by running: `sudo apt install certbot python3-certbot-nginx -y && sudo certbot --nginx`
