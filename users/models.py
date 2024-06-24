import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


def file_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'avatar_{instance.username}.{ext}'
    return os.path.join('avatars/', filename)


class CustomUser(AbstractUser):
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.ImageField(upload_to=file_upload, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

