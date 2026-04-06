# Changelog

All notable changes to the WriteSpace project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2024-01-01

### Added

- **Public Landing Page**: Hero section with call-to-action, feature highlights, and latest posts preview for unauthenticated visitors.
- **Authentication Flows**: Login and registration forms with validation, automatic redirection based on user role, and secure logout.
- **Role-Based Access Control**: Two-tier role system (User and Admin) using Django's built-in `is_staff` flag. Admins access the dashboard and user management; regular users access blog reading and writing.
- **Blog CRUD with Ownership**: Authenticated users can create, read, update, and delete blog posts. Edit and delete actions are restricted to post authors and admin users. Posts use UUID primary keys.
- **Admin Dashboard**: Overview panel displaying total posts, total users, and recent posts table with quick action links for writing posts, managing users, and browsing blogs.
- **User Management**: Admin-only interface to create new users with role assignment (User or Admin) and delete existing users. Self-deletion and default admin deletion are prevented.
- **Avatar System**: Custom template tag (`{% render_avatar user %}`) rendering role-based emoji avatars with display names — crown emoji for admins, book emoji for regular users.
- **Responsive Tailwind UI**: Fully responsive design using Tailwind CSS via CDN. Mobile-friendly navigation, card grids, tables with mobile card fallbacks, and modal dialogs.
- **Vercel Serverless Deployment**: Configuration for Vercel deployment with automatic static file collection, database migration, and default admin creation on cold start via `wsgi.py`.
- **WhiteNoise Static Files**: Static file serving via WhiteNoise with compressed manifest storage for production environments.
- **Signed Cookie Sessions**: Session engine configured to use signed cookies, eliminating the need for a session database table.
- **Environment Configuration**: Settings driven by environment variables with sensible defaults. Supports `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- **PostgreSQL Support**: Database configuration via `dj-database-url` with automatic fallback to SQLite for local development.
- **Custom Management Command**: `create_default_admin` command for provisioning the initial superuser from environment variables.
- **Error Pages**: Custom 404 and 500 error templates with consistent branding and navigation links.