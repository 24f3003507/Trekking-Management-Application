# Trekking Management Application

A Flask-based web application for managing trekking activities. The system supports three types of users:

- **Admin**
- **Trek Staff**
- **Users**

The application allows users to browse and book treks, while admins can manage treks, users, and staff assignments.

---

## Features

- User Registration and Login
- Admin Dashboard
- Staff Dashboard
- Trek Management
- Trek Booking
- User Profile Management
- Booking History
- SQLite Database using SQLAlchemy

---

## Technologies Used

- Python 3
- Flask
- Flask-SQLAlchemy
- HTML
- CSS
- Jinja2
- SQLite

---

## Project Structure

```
Trekking-Management-Application/
│
├── backend/
│   ├── controllers.py
│   └── models.py
│
├── static/
├── templates/
├── instance/
├── app.py
├── README.md
└── requirements.txt
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Trekking-Management-Application
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the required packages manually:

```bash
pip install flask flask-sqlalchemy
```

---

## Running the Application

Start the Flask application by running:

```bash
python app.py
```

The server will start on:

```
http://127.0.0.1:5003
```

Open the above URL in your browser.

---

## Database

The application uses **SQLite**.

On the first run:

- The SQLite database is created automatically.
- All required tables are generated using:

```python
db.create_all()
```

The database file will be created inside the project directory (or the configured `instance` folder).

---

## Login

Register a new account using the registration page.

Depending on the user role, the application redirects to:

- Admin Dashboard
- Staff Dashboard
- User Dashboard

---

## Important Notes

- Activate the virtual environment before running the application.
- Ensure all dependencies are installed.
- Do not delete the SQLite database unless you want to reset all stored data.
- The application runs in debug mode during development.

---

## Author

**Suraj Kumar**

B.Tech CSE | BS in Data Science and Applications