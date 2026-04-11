from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path)

        if img.height > 1000 or img.width > 1000:
            new_img = (1000, 1000)
            img.thumbnail(new_img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(self.avatar.path)