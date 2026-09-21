from django.db import models
from django.conf import settings
from content.models import Video

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'video']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - Bookmark: {self.video.title}"


class WatchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watch_histories')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='watch_histories')
    seconds_watched = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'video']
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - History: {self.video.title} ({self.seconds_watched}s)"
