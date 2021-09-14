from django.db import models
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    # Change to encrypted fields later
    YTHeaders = models.CharField(max_length=10000, null=True, blank=True)
    SpotifyAPIKey = models.CharField(max_length=1000, null=True, blank=True)
    SpotifyRefreshToken = models.CharField(max_length=1000, null=True, blank=True)
    AppleMusicAPIKey = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self) -> str:
        return self.username 
