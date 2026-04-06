# Accounts models
# This app uses Django's built-in auth.User model for authentication and authorization.
# - auth.User.first_name is used as the display name
# - auth.User.is_staff distinguishes admin users from regular users
# No custom user model is needed for this application.

from django.db import models  # noqa: F401