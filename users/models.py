import os

from django.contrib.postgres.indexes import HashIndex
from django.core import validators
from django_resized import ResizedImageField
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError

from core.settings import BIRTH_YEAR_MIN, BIRTH_YEAR_MAX


def file_upload(instance, filename):
    """ This function is used to upload the user's avatar. """
    ext = filename.split('.')[-1]
    filename = f'{instance.username}.{ext}'
    return os.path.join('users/avatars/', filename)


class CustomUser(AbstractUser):
    """  This model represents a custom user. """
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = ResizedImageField(size=[300, 300], crop=['top', 'left'], upload_to=file_upload, blank=True)
    birth_year = models.IntegerField(
        validators=[  # first option for checking birth year range
            validators.MinValueValidator(BIRTH_YEAR_MIN),
            validators.MaxValueValidator(BIRTH_YEAR_MAX)
        ],
        null=True,
        blank=True
    )

    def clean(self):  # second option for checking birth year range
        super().clean()
        if self.birth_year and not (BIRTH_YEAR_MIN < self.birth_year < BIRTH_YEAR_MAX):
            raise ValidationError(
                f"Tug'ilgan yili {BIRTH_YEAR_MIN} yildan katta va {BIRTH_YEAR_MAX} yilgacha bo'lishi kerak."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "user"  # database table name
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]  # descending order by date joined
        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            HashIndex(fields=['middle_name'], name='%(class)s_middle_name_hash_idx'),
            models.Index(fields=['username'], name='%(class)s_username_idx'),
        ]
        constraints = [
            models.CheckConstraint(  # third option for checking birth year range
                check=models.Q(birth_year__gt=BIRTH_YEAR_MIN) & models.Q(birth_year__lt=BIRTH_YEAR_MAX),
                name='check_birth_year_range'
            )
        ]

    def get_full_name(self):
        """ This method returns the full name of the user"""
        if self.full_name:
            return self.full_name
        else:
            return super().get_full_name()

    def __str__(self):
        """ This method returns the full name of the user"""
        if self.full_name:
            return self.full_name
        else:
            return self.email or self.username

    @property
    def full_name(self):
        """ Returns the user's full name. """
        return f"{self.last_name} {self.first_name} {self.middle_name}"
