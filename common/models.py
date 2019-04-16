from django.db import models

from accounts.utils import generate_photo_profile_path


class Image(models.Model):
    image = models.ImageField(upload_to=generate_photo_profile_path)
    created_at = models.DateTimeField(auto_now_add=True)
