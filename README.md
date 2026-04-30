![bannerLiquidGlass](https://github.com/imaquar/PlanBoost/blob/main/static/images/bannerLiquidGlass.jpg)

# PlanBoost

PlanBoost is a Django web application for personal productivity that combines `tasks`, `notes`, a `Pomodoro timer`, a statistics `dashboard`, and a user module for registration, authentication, and profile management (`users`).

## Tech Stack

- Python 3.13
- Django 4.0+
- SQLite (default)
- HTML/CSS/JavaScript
- Pillow (user avatars)

## Features

- Registration, login, logout, password change, and profile with avatar
- Full CRUD for tasks and notes
- Dashboard with upcoming tasks, recent notes, and completed-task stats for today and the last 7 days
- Pomodoro timer
- Light/dark theme switcher with saved user preference

## AJAX in the project

Partial updates are implemented without full page reloads: in `tasks`, status changes, filtering, and sorting are handled via AJAX; in `dashboard`, stats, tasks, and notes blocks are auto-refreshed.

## Project structure

```text
PlanBoost/
├── dashboard/
├── notes/
├── tasks/
├── timer/
├── users/
├── templates/
├── static/
├── media/
├── planBoost/
├── db.sqlite3
└── manage.py
```

## Local setup

1. Clone the repository and enter the project directory:
```bash
git clone https://github.com/imaquar/PlanBoost.git
cd PlanBoost
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
```

3. Activate the virtual environment:
```bash
. .venv/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install -U Django Pillow
```

5. Apply migrations:
```bash
python manage.py migrate
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## URL routes

- `/` — dashboard
- `/tasks/` — tasks
- `/notes/` — notes
- `/timer/` — timer
- `/users/register/`, `/users/login/`, `/users/profile/`, `/users/password_change/`

## Static and media files

- `STATIC_URL = /static/`
- `MEDIA_URL = /media/`

## Notes

- Authentication is required for dashboard, tasks, notes, timer, and profile pages
- Current project timezone: `Europe/Moscow`
- Default database: `db.sqlite3`
