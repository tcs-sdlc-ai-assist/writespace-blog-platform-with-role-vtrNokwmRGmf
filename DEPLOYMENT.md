# Deployment Guide

This guide covers deploying WriteSpace to **Vercel** with a **Neon PostgreSQL** database. It includes environment variable configuration, cold-start behavior, static file handling, and troubleshooting tips.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Neon PostgreSQL Setup](#neon-postgresql-setup)
3. [Vercel Setup](#vercel-setup)
4. [Environment Variables](#environment-variables)
5. [vercel.json Explained](#verceljson-explained)
6. [Cold-Start Behavior](#cold-start-behavior)
7. [Static File Handling](#static-file-handling)
8. [Local Development](#local-development)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A [Vercel](https://vercel.com) account (free tier works)
- A [Neon](https://neon.tech) account (free tier works)
- Git repository with the WriteSpace codebase pushed to GitHub, GitLab, or Bitbucket
- Python 3.12 compatible runtime

---

## Neon PostgreSQL Setup

[Neon](https://neon.tech) provides serverless PostgreSQL databases that pair well with Vercel's serverless functions.

### Step 1: Create a Neon Project

1. Sign in to [Neon Console](https://console.neon.tech).
2. Click **New Project**.
3. Choose a project name (e.g., `writespace`).
4. Select the region closest to your Vercel deployment region (e.g., `us-east-1` for Vercel's default `iad1`).
5. Click **Create Project**.

### Step 2: Get the Connection String

1. After project creation, Neon displays the connection details.
2. Copy the **connection string** in the format:

   ```
   postgres://<user>:<password>@<host>/<database>?sslmode=require
   ```

3. This value will be used as the `DATABASE_URL` environment variable.

> **Important:** Neon requires SSL connections. Ensure `?sslmode=require` is appended to the connection string. Neon typically includes this by default.

### Step 3: Verify Connectivity (Optional)

You can test the connection locally before deploying:

```bash
# Install psql or use any PostgreSQL client
psql "postgres://<user>:<password>@<host>/<database>?sslmode=require"
```

---

## Vercel Setup

### Step 1: Import the Repository

1. Sign in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New** → **Project**.
3. Import your Git repository containing the WriteSpace codebase.
4. Vercel will auto-detect the project. No framework preset is needed — the `vercel.json` file handles the build configuration.

### Step 2: Set the Root Directory

If your repository root contains the `writespace/` project directory and `vercel.json` is at the repository root, Vercel will pick it up automatically. No root directory override is needed.

### Step 3: Configure Environment Variables

Before deploying, add all required environment variables in the Vercel project settings. See the [Environment Variables](#environment-variables) section below.

### Step 4: Deploy

1. Click **Deploy**.
2. Vercel will build the project using the `@vercel/python` builder as specified in `vercel.json`.
3. On the first cold start, the WSGI entrypoint will automatically:
   - Run `collectstatic` to gather static files
   - Run `migrate` to apply database migrations
   - Create the default admin superuser if one does not exist

### Step 5: Verify Deployment

1. Visit your Vercel deployment URL (e.g., `https://writespace-xxxx.vercel.app`).
2. You should see the WriteSpace landing page.
3. Log in with the admin credentials you configured in the environment variables.

---

## Environment Variables

Configure these environment variables in your Vercel project settings under **Settings** → **Environment Variables**. Set them for **Production**, **Preview**, and **Development** environments as needed.

| Variable | Required | Description | Example |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key for cryptographic signing. Must be a long, random, unique string. **Never reuse across environments.** | `a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9` |
| `DATABASE_URL` | **Yes** | PostgreSQL connection string from Neon. | `postgres://user:pass@ep-cool-name-123456.us-east-1.aws.neon.tech/dbname?sslmode=require` |
| `DJANGO_SUPERUSER_USERNAME` | **Yes** | Username for the default admin account created on first deploy. | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | **Yes** | Password for the default admin account. Use a strong password in production. | `MyStr0ngP@ssw0rd!` |
| `ALLOWED_HOSTS` | No | Comma-separated list of allowed hostnames. `.vercel.app` is automatically appended by settings. | `writespace.example.com` |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated list of trusted origins for CSRF. `https://*.vercel.app` is automatically appended. | `https://writespace.example.com` |
| `DEBUG` | No | Set to `False` in production. Defaults to `False`. | `False` |
| `DJANGO_SETTINGS_MODULE` | No | Django settings module path. Defaults to `writespace.settings`. | `writespace.settings` |

### Generating a SECRET_KEY

You can generate a secure secret key using Python:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or without Django installed:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Custom Domain Configuration

If you add a custom domain to your Vercel project:

1. Add the domain to `ALLOWED_HOSTS` (e.g., `writespace.example.com`).
2. Add the full origin to `CSRF_TRUSTED_ORIGINS` (e.g., `https://writespace.example.com`).

---

## vercel.json Explained

The `vercel.json` file configures how Vercel builds and routes requests:

```json
{
  "builds": [
    {
      "src": "writespace/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "writespace/wsgi.py"
    }
  ]
}
```

### Builds

- **`src`**: Points to the WSGI entrypoint (`writespace/wsgi.py`). This is the file Vercel uses to create the serverless function.
- **`use`**: Specifies the `@vercel/python` builder, which installs dependencies from `requirements.txt` and packages the application.
- **`maxLambdaSize`**: Set to `15mb` to accommodate Django and all dependencies. The default limit is `50mb`, but keeping it smaller improves cold-start times.

### Routes

- **`src: "/(.*)"` → `dest: "writespace/wsgi.py"`**: All incoming requests are routed to the Django WSGI application. Django's URL routing (`writespace/urls.py`) handles dispatching to the correct view.

### How It Works

1. Vercel installs Python dependencies from `requirements.txt`.
2. The `writespace/wsgi.py` file is packaged as a serverless function.
3. Every HTTP request hits the serverless function, which runs Django's full request/response cycle.
4. Static files are served by WhiteNoise middleware (see [Static File Handling](#static-file-handling)).

---

## Cold-Start Behavior

Vercel serverless functions have a **cold start** — the first request after a period of inactivity initializes the runtime. WriteSpace's `wsgi.py` performs several setup tasks during cold start:

### What Happens on Cold Start

1. **`collectstatic --noinput`**: Gathers all static files into the `staticfiles/` directory. WhiteNoise then serves them from memory.
2. **`migrate --noinput`**: Applies any pending database migrations to the Neon PostgreSQL database.
3. **Default admin creation**: Checks if a user with the `DJANGO_SUPERUSER_USERNAME` exists. If not, creates a superuser with the configured credentials.

### Error Handling

Each cold-start step is wrapped in a `try/except` block. If any step fails (e.g., database is temporarily unreachable), the failure is silently caught and the application still starts. This prevents a single migration error from taking down the entire application.

### Performance Considerations

- **Cold starts** typically take 2–5 seconds depending on the database connection time.
- **Warm requests** (subsequent requests while the function is still active) are fast since Django is already initialized.
- Neon databases on the free tier may also have their own cold start if the compute endpoint has been suspended due to inactivity. This can add 1–3 seconds to the first request.
- To minimize cold starts, consider upgrading to Vercel Pro (longer function retention) and Neon Pro (always-on compute).

### Session Handling

WriteSpace uses **signed cookie sessions** (`SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'`). This means:

- No session table is needed in the database.
- Sessions survive across cold starts without any additional configuration.
- Session data is stored in the user's browser cookie, signed with the `SECRET_KEY`.

> **Warning:** Changing the `SECRET_KEY` will invalidate all existing sessions, logging out all users.

---

## Static File Handling

WriteSpace uses [WhiteNoise](http://whitenoise.evans.io/) to serve static files directly from the Python application, eliminating the need for a separate static file server or CDN.

### How It Works

1. **Middleware**: `whitenoise.middleware.WhiteNoiseMiddleware` is included in `MIDDLEWARE` after `SecurityMiddleware`.
2. **Collection**: `collectstatic` gathers files from `static/` and all app static directories into `staticfiles/`.
3. **Storage**: `CompressedManifestStaticFilesStorage` adds content hashes to filenames (e.g., `style.abc123.css`) for cache busting and serves gzip/brotli compressed versions.
4. **Serving**: WhiteNoise serves static files with proper caching headers directly from the serverless function.

### Configuration in Settings

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Why WhiteNoise?

- **No external CDN required**: Static files are served from the same serverless function.
- **Automatic compression**: Files are compressed with gzip and brotli at build time.
- **Cache-friendly**: Content-hashed filenames allow aggressive browser caching.
- **Zero configuration**: Works out of the box with Django on Vercel.

### Tailwind CSS

WriteSpace loads Tailwind CSS via CDN (`https://cdn.tailwindcss.com`) in the base template. This is a development/prototyping approach. For production optimization, consider:

- Using the Tailwind CLI to generate a production CSS build.
- Placing the compiled CSS in `static/css/` and referencing it with `{% static 'css/tailwind.css' %}`.

---

## Local Development

### Step 1: Clone and Install

```bash
git clone <your-repo-url>
cd writespace
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

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

### Step 3: Run Migrations and Create Admin

```bash
cd writespace
python manage.py migrate
python manage.py create_default_admin
```

### Step 4: Start the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

---

## Troubleshooting

### "DisallowedHost" Error

**Symptom:** You see `Invalid HTTP_HOST header` in the browser.

**Fix:** Add your deployment domain to the `ALLOWED_HOSTS` environment variable. For Vercel deployments, `.vercel.app` is automatically appended, but custom domains must be added manually.

```
ALLOWED_HOSTS=writespace.example.com,www.writespace.example.com
```

### "CSRF Verification Failed" Error

**Symptom:** Form submissions fail with a 403 CSRF error.

**Fix:** Add your deployment origin to `CSRF_TRUSTED_ORIGINS`. The value must include the scheme (`https://`).

```
CSRF_TRUSTED_ORIGINS=https://writespace.example.com
```

### Database Connection Errors

**Symptom:** 500 errors on pages that query the database.

**Possible causes:**
1. `DATABASE_URL` is not set or is incorrect.
2. Neon compute endpoint is suspended (free tier). The first request may time out — try refreshing.
3. SSL mode is missing. Ensure `?sslmode=require` is in the connection string.

**Fix:** Verify the `DATABASE_URL` in Vercel environment variables matches the Neon connection string exactly.

### Migrations Not Applied

**Symptom:** "relation does not exist" or "no such table" errors.

**Possible causes:**
1. The cold-start migration in `wsgi.py` failed silently.
2. The database was recreated without running migrations.

**Fix:** You can manually trigger migrations by redeploying (which triggers a new cold start) or by running migrations locally against the Neon database:

```bash
DATABASE_URL="postgres://user:pass@host/db?sslmode=require" python manage.py migrate
```

### Admin User Not Created

**Symptom:** Cannot log in with the configured admin credentials.

**Possible causes:**
1. `DJANGO_SUPERUSER_USERNAME` or `DJANGO_SUPERUSER_PASSWORD` environment variables are not set.
2. A user with that username already exists (the creation is skipped).

**Fix:** Verify environment variables are set. If the user exists but the password is unknown, connect to the database and reset it:

```bash
DATABASE_URL="postgres://user:pass@host/db?sslmode=require" python manage.py changepassword admin
```

### Static Files Not Loading (404 on /static/)

**Symptom:** CSS/JS files return 404 errors.

**Possible causes:**
1. `collectstatic` failed during cold start.
2. `whitenoise` is not in `requirements.txt` or `MIDDLEWARE`.

**Fix:** Ensure `whitenoise` is listed in `requirements.txt` and `WhiteNoiseMiddleware` is in `MIDDLEWARE` after `SecurityMiddleware`. Redeploy to trigger a fresh `collectstatic`.

### Slow First Request

**Symptom:** The first request after a period of inactivity takes 3–10 seconds.

**Cause:** This is expected behavior due to:
1. Vercel serverless function cold start (Python runtime initialization).
2. Neon compute endpoint wake-up (free tier suspends after 5 minutes of inactivity).
3. `collectstatic`, `migrate`, and admin creation running on cold start.

**Mitigation:**
- Upgrade to Neon Pro for always-on compute.
- Upgrade to Vercel Pro for longer function retention.
- Keep the function warm with a periodic health check ping (e.g., using an external cron service).

### "Module Not Found" Errors

**Symptom:** `ModuleNotFoundError` in Vercel build logs.

**Fix:** Ensure all dependencies are listed in `requirements.txt` at the repository root. Vercel installs packages from this file during the build step.

### Build Exceeds Lambda Size Limit

**Symptom:** Vercel build fails with "Lambda size exceeds maximum".

**Fix:** The `maxLambdaSize` in `vercel.json` is set to `15mb`. If your dependencies grow beyond this:
1. Remove unused packages from `requirements.txt`.
2. Increase `maxLambdaSize` (maximum is `50mb`).

---

## Deployment Checklist

Before deploying to production, verify:

- [ ] `SECRET_KEY` is set to a unique, random value (not the default)
- [ ] `DEBUG` is set to `False`
- [ ] `DATABASE_URL` points to your Neon PostgreSQL database
- [ ] `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` are set with strong credentials
- [ ] `ALLOWED_HOSTS` includes your custom domain (if applicable)
- [ ] `CSRF_TRUSTED_ORIGINS` includes your custom domain with `https://` prefix (if applicable)
- [ ] All dependencies are listed in `requirements.txt`
- [ ] `vercel.json` is present at the repository root
- [ ] The Neon database region matches or is close to the Vercel deployment region