from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import logging

User = get_user_model()  # Get the custom User model if you're using one, else it defaults to Django's User model
logger = logging.getLogger(__name__)

class UsernameBackend(BaseBackend):
    """
    Custom Authentication Backend to authenticate using a username and password.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # Fetch the user by username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"Authentication failed: No user found with username {username}.")
            return None  # Return None if the user doesn't exist

        # Check if the password is correct
        if user.check_password(password):
            logger.info(f"User {user.username} authenticated successfully.")
            return user
        else:
            logger.warning(f"Authentication failed: Incorrect password for username {username}.")
            return None  # Explicitly return None if password check fails

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"User with ID {user_id} does not exist.")
            return None  # Return None if user doesn't exist
