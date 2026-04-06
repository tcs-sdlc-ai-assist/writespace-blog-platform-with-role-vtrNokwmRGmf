# WriteSpace

A clean, modern blogging platform built with Django where writers can create, share, and discover amazing content. Features role-based access control, an admin dashboard, user management, and a responsive Tailwind CSS interface — deployable to Vercel with a Neon PostgreSQL database.

---

## Features

- **Public Landing Page** — Hero section with call-to-action, feature highlights, and latest posts preview for unauthenticated visitors.
- **Authentication** — Login and registration with form validation, automatic redirection based on user role, and secure logout.
- **Role-Based Access Control** — Two-tier role system (User and Admin) using Django's built-in `is_staff` flag. Admins access the dashboard and user management; regular users access blog reading and writing.
- **Blog CRUD with Ownership** — Authenticated users can create, read, update, and delete blog posts. Edit and delete actions are restricted to post authors and admin users. Posts use UUID primary keys.
- **Admin Dashboard** — Overview panel displaying total posts, total users, and recent posts table with quick action links.
- **User Management** — Admin-only interface to create new users with role assignment and delete existing users. Self-deletion and default admin deletion are prevented.
- **Avatar System** — Custom template tag (`{% render_avatar user %}`) rendering role-based emoji avatars with display names.
- **Responsive UI** — Fully responsive design using Tailwind CSS via CDN with mobile-friendly navigation, card grids, tables with mobile card fallbacks, and modal dialogs.
- **Vercel Serverless Deployment** — Configuration for Vercel with automatic static file collection, database migration, and default admin creation on cold start.
- **WhiteNoise Static Files** — Static file serving via WhiteNoise with compressed manifest storage for production.
- **Signed Cookie Sessions** — No session database table required; sessions are stored in signed browser cookies.
- **Custom Error Pages** — Branded 404 and 500 error templates with navigation links.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 5.0+ |
| Database | PostgreSQL (Neon) / SQLite (local fallback) |
| Styling | Tailwind CSS (CDN) |
| Static Files | WhiteNoise |
| Deployment | Vercel (serverless) |
| DB URL Parsing | dj-database-url |
| Environment | python-dotenv |

---

## Project Structure

```
writespace/
├── accounts/                        # Authentication app
│   ├── management/
│   │   └── commands/
│   │       └── create_default_admin.py
│   ├── templatetags/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                     # LoginForm, RegistrationForm, AdminCreateUserForm
│   ├── models.py                    # Uses Django's built-in auth.User
│   ├── urls.py
│   └── views.py                     # login, register, logout views
├── blog/                            # Blog app
│   ├── templatetags/
│   │   └── avatar_tags.py           # render_avatar template tag
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                     # PostForm (ModelForm)
│   ├── models.py                    # Post model (UUID primary key)
│   ├── urls.py
│   └── views.py                     # landing, blog CRUD, admin dashboard, user management
├── static/                          # Static assets (collected by WhiteNoise)
├── templates/                       # Global templates
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   ├── blog/
│   │   ├── admin_dashboard.html
│   │   ├── blog_confirm_delete.html
│   │   ├── blog_detail.html
│   │   ├── blog_form.html
│   │   ├── blog_list.html
│   │   ├── landing.html
│   │   └── user_management.html
│   ├── base.html
│   ├── 404.html
│   └── 500.html
├── writespace/                      # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py                      # WSGI entrypoint (cold-start setup)
└── manage.py
├── .env.example                     # Environment variable template
├── requirements.txt                 # Python dependencies
├── vercel.json                      # Vercel deployment configuration
├── CHANGELOG.md
├── DEPLOYMENT.md
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- pip
- PostgreSQL (optional — SQLite is used as a fallback)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd writespace
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and edit it with your local settings:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-local-secret-key
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@localhost:5432/writespace
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=changeme123
DJANGO_SETTINGS_MODULE=writespace.settings
```

> **Note:** If you omit `DATABASE_URL`, Django will fall back to SQLite (`db.sqlite3`), which is fine for local development.

### 5. Run Migrations

```bash
cd writespace
python manage.py migrate
```

### 6. Create the Default Admin User

```bash
python manage.py create_default_admin
```

This reads `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` from your environment and creates a superuser if one does not already exist.

### 7. Start the Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to access the application.

---

## Vercel Deployment

WriteSpace is configured for deployment on Vercel with a Neon PostgreSQL database. See [DEPLOYMENT.md](DEPLOYMENT.md) for the full deployment guide, including:

- Neon PostgreSQL setup
- Vercel project configuration
- Environment variable reference
- Cold-start behavior
- Static file handling
- Troubleshooting

---

## URL Route Map

| URL Pattern | View | Name | Auth Required | Description |
|---|---|---|---|---|
| `/` | `landing_page` | `landing` | No | Public landing page (redirects authenticated users) |
| `/login/` | `login_view` | `login` | No | User login |
| `/register/` | `register_view` | `register` | No | User registration |
| `/logout/` | `logout_view` | `logout` | No | Logout (redirects to landing) |
| `/blogs/` | `blog_list` | `blog_list` | Yes | List all blog posts |
| `/blog/<uuid:id>/` | `blog_detail` | `blog_detail` | Yes | View a single blog post |
| `/write/` | `blog_create` | `blog_create` | Yes | Create a new blog post |
| `/edit/<uuid:id>/` | `blog_edit` | `blog_edit` | Yes | Edit a blog post (owner or admin) |
| `/delete/<uuid:id>/` | `blog_delete` | `blog_delete` | Yes | Delete a blog post (owner or admin) |
| `/admin-panel/` | `admin_dashboard` | `admin_dashboard` | Admin | Admin dashboard overview |
| `/users/` | `user_management` | `user_management` | Admin | Create and manage users |
| `/admin/` | Django Admin | — | Superuser | Built-in Django admin interface |

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | `django-insecure-change-me-in-production` | Django secret key for cryptographic signing |
| `DEBUG` | No | `False` | Enable debug mode (`True` for local development) |
| `DATABASE_URL` | No | SQLite fallback | PostgreSQL connection string |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | No | `http://localhost:8000,http://127.0.0.1:8000` | Comma-separated trusted origins for CSRF |
| `DJANGO_SUPERUSER_USERNAME` | No | `admin` | Username for the default admin account |
| `DJANGO_SUPERUSER_PASSWORD` | No | `changeme123` | Password for the default admin account |
| `DJANGO_SETTINGS_MODULE` | No | `writespace.settings` | Django settings module path |

Generate a secure `SECRET_KEY` for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## License

This project is proprietary software. All rights reserved. Unauthorized copying, distribution, or modification of this project, via any medium, is strictly prohibited without prior written permission from the project owner.