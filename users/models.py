import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.manager import UserManager


class User(AbstractUser):
    username = None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()