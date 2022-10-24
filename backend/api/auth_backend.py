from django.contrib.auth.backends import ModelBackend
from .models import User


class PasswordLessAuthBackend(ModelBackend):
    """Log in to Django without providing a password.

    """

    def authenticate(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
