from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class Chapter(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Topic(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['chapter', 'slug']

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"


class Playlist(models.Model):
    youtube_playlist_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    item_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Video(models.Model):
    SOURCE_YOUTUBE = 'youtube'
    SOURCE_BUNNY = 'bunny'
    SOURCE_CHOICES = [
        (SOURCE_YOUTUBE, 'YouTube'),
        (SOURCE_BUNNY, 'Bunny Stream'),
    ]

    CONTENT_TYPE_CONCEPT = 'Concept'
    CONTENT_TYPE_PYQ = 'PYQ'
    CONTENT_TYPE_PROBLEM_SOLVING = 'Problem Solving'
    CONTENT_TYPE_ADVANCED_PROBLEM = 'Advanced Problem'
    CONTENT_TYPE_REVISION = 'Revision'
    CONTENT_TYPE_STRATEGY = 'Strategy'
    CONTENT_TYPE_OTHER = 'Other'
    CONTENT_TYPE_CHOICES = [
        (CONTENT_TYPE_CONCEPT, 'Concept'),
        (CONTENT_TYPE_PYQ, 'PYQ'),
        (CONTENT_TYPE_PROBLEM_SOLVING, 'Problem Solving'),
        (CONTENT_TYPE_ADVANCED_PROBLEM, 'Advanced Problem'),
        (CONTENT_TYPE_REVISION, 'Revision'),
        (CONTENT_TYPE_STRATEGY, 'Strategy'),
        (CONTENT_TYPE_OTHER, 'Other'),
    ]

    DIFFICULTY_EASY = 'Easy'
    DIFFICULTY_MEDIUM = 'Medium'
    DIFFICULTY_HARD = 'Hard'
    DIFFICULTY_ADVANCED = 'Advanced'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Easy'),
        (DIFFICULTY_MEDIUM, 'Medium'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_ADVANCED, 'Advanced'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_YOUTUBE)
    youtube_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    bunny_library_id = models.CharField(max_length=100, null=True, blank=True)
    bunny_video_id = models.CharField(max_length=100, null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    duration_sec = models.IntegerField(default=0)
    is_short = models.BooleanField(default=False)
    thumbnail_url = models.URLField(max_length=1000, blank=True, null=True)
    pdf_url = models.URLField(max_length=1000, blank=True, null=True)

    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')

    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default=CONTENT_TYPE_OTHER)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_MEDIUM)
    pyq_year = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    search_vector = SearchVectorField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_source_display()})"


class LiveSession(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_LIVE = 'live'
    STATUS_ENDED = 'ended'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_LIVE, 'Live'),
        (STATUS_ENDED, 'Ended'),
    ]

    SOURCE_YOUTUBE = 'youtube'
    SOURCE_MANAGED = 'managed'
    SOURCE_CHOICES = [
        (SOURCE_YOUTUBE, 'YouTube Live'),
        (SOURCE_MANAGED, 'Managed Stream'),
    ]

    title = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_YOUTUBE)
    stream_id = models.CharField(max_length=255, blank=True, null=True)
    recording_link = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name='live_sessions')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"Live: {self.title} ({self.get_status_display()})"
