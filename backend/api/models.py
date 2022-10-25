import datetime

import django
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


# hook in the New Manager to our Model
# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    province = models.CharField(max_length=255, default="Tehran")
    city = models.CharField(max_length=255, default="Tehran")
    phone = models.CharField(max_length=255, default="989000000")
    fullname = models.CharField(max_length=300, default="John Doe")
    is_oauth = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # an admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    iban_id = models.CharField(max_length=255, default="")
    credit_id = models.CharField(max_length=255, default="")
    id_card = models.CharField(max_length=255, unique=True)
    ref_id = models.CharField(max_length=255, unique=True)
    ref_used = models.BooleanField(default=False)
    ref_used_id = models.CharField(max_length=255, default="")
    sold_coins = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    money_balance = models.IntegerField(default=0)

    objects = UserManager()
    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.staff

    @property
    def is_admin(self):
        """Is the user an admin member?"""
        return self.admin

    def is_profile_completed(self):
        if self.iban_id != "" and self.id_card != "" and self.id_card != "":
            return True
        return False

    @staticmethod
    def is_referral_valid(ref_code):
        try:
            user = User.objects.get(ref_id=ref_code)
            print(f"[Referral][{user.id}]: ref: {ref_code}")
            return True
        except User.DoesNotExist:
            return False


class Offer(models.Model):
    auto_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    date = models.DateField(default=datetime.date.today)
    amount = models.IntegerField(default=0)
    server = models.CharField(default="", max_length=255)

    def __str__(self):
        return f"offer{self.auto_id}-u{self.user.id}"


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tr_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tr_receiver')
    amount = models.IntegerField(default=0)
    date = models.DateField(default=datetime.date.today)
    status = models.CharField(default="Pending", max_length=255)

    def __str__(self):
        return f"tr{self.id}-s{self.sender.id}-r{self.receiver.id}"


class Request(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rq_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rq_receiver')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='rq_offer')
    amount = models.IntegerField(default=0)
    date = models.DateField(default=datetime.date.today)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"tr{self.id}-s{self.sender.id}-r{self.receiver.id}"


class Ticket(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    message = models.TextField()
    subject = models.CharField(max_length=300)

# class Chat(models.Model):
#     parti1 = models.ForeignKey(User, models.CASCADE)
#     part2 = models.ForeignKey(User, models.CASCADE)
