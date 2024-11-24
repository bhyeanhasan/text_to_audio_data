from django.db import models
from django.contrib.auth.models import User


class TextToAudio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    char_count = models.IntegerField(null=True, blank=True)
    is_converted = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)
    audio = models.FileField(upload_to='audios/', null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
