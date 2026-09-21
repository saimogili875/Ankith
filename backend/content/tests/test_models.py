import pytest
from django.utils import timezone
from content.models import Chapter, Topic, Video, LiveSession
from progress.models import Bookmark, WatchHistory
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_chapter_and_topic():
    chapter = Chapter.objects.create(name='Calculus', slug='calculus', sort_order=1)
    topic = Topic.objects.create(chapter=chapter, name='Limits', slug='limits', sort_order=1)
    assert str(chapter) == 'Calculus'
    assert str(topic) == 'Calculus - Limits'
    assert topic.chapter == chapter

@pytest.mark.django_db
def test_create_youtube_and_bunny_videos():
    yt_video = Video.objects.create(
        source=Video.SOURCE_YOUTUBE,
        youtube_id='abc12345',
        title='Calculus Limits Overview',
        duration_sec=120,
        is_short=True
    )
    bunny_video = Video.objects.create(
        source=Video.SOURCE_BUNNY,
        bunny_library_id='lib99',
        bunny_video_id='vid888',
        title='Advanced Integration Class',
        duration_sec=3600,
        is_short=False
    )
    assert yt_video.source == 'youtube'
    assert yt_video.is_short is True
    assert bunny_video.source == 'bunny'
    assert bunny_video.bunny_library_id == 'lib99'

@pytest.mark.django_db
def test_live_session_model():
    video = Video.objects.create(
        title='Live Stream Recording',
        duration_sec=3600
    )
    session = LiveSession.objects.create(
        title='Calculus Live Q&A',
        scheduled_time=timezone.now(),
        status=LiveSession.STATUS_SCHEDULED,
        source=LiveSession.SOURCE_YOUTUBE,
        recording_link=video
    )
    assert 'Calculus Live Q&A' in str(session)
    assert session.recording_link == video

@pytest.mark.django_db
def test_bookmark_and_watch_history():
    user = User.objects.create_user(username='student1', password='pass123password')
    video = Video.objects.create(title='Matrix Operations', duration_sec=600)
    
    bookmark = Bookmark.objects.create(user=user, video=video)
    history = WatchHistory.objects.create(user=user, video=video, seconds_watched=300, completed=False)

    assert bookmark.user == user
    assert history.seconds_watched == 300
