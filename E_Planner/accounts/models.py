import uuid
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator
from django.db import models
from django.utils import timezone

letters_only = RegexValidator(
    regex=r'^[A-Za-zА-Яа-я]+([ -][A-Za-zА-Яа-я]+)*$',
    message='Use only letters, spaces and hyphens.'
)


phone_validator = RegexValidator(regex=r'^\+?[0-9]{7,15}$', message='Enter a valid phone number.')


def calculate_age(birth_date):
    today = timezone.localdate()

    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def validate_image_size(image):
    if image.size > 2 * 1024 * 1024:
        raise ValidationError('Image must be smaller than 2MB')


def validate_birth_date(value):
    today = date.today()
    if value > today:
        raise ValidationError('Birth date cannot be in the future')

    if calculate_age(value) < 16:
        raise ValidationError('You must be at least 16 years old')


def avatar_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    unique_filename = f'{uuid.uuid4()}{extension}'

    return f'avatars/{instance.user_id}/{unique_filename}'


class AppUser(AbstractUser):
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True, validators=[validate_birth_date])
    phone_number = models.CharField(max_length=16, blank=True, validators=[phone_validator])
    city = models.CharField(max_length=50, blank=True, validators=[letters_only])
    nickname = models.CharField(max_length=30, blank=True, validators=[MinLengthValidator(3)])
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, validators=[validate_image_size, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])])
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def age(self):
        if not self.birth_date:
            return None

        return calculate_age(self.birth_date)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.user.username
