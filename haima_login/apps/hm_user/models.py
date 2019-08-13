from django.db import models
from django.contrib.auth.models import AbstractUser


class Hm_User(AbstractUser):
    phone = models.CharField(max_length=11)
