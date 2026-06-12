from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.templatetags.static import static

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', blank=True, null=True,)
    displayname = models.CharField(max_length=200, blank=True)
    info = models.TextField(null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    @property
    def name(self):
        return self.displayname if self.displayname else self.user.username
    
    @property
    def avatar(self):
        if self.image:
            return self.image.url
        else:
            return static('images/default_avatar.png')