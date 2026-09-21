import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.base import BaseStorage
from django.test import RequestFactory
from content.models import Video
from content.admin import VideoAdmin, approve_selected, set_difficulty_hard, set_content_concept

class DummyStorage(BaseStorage):
    def _get(self, *args, **kwargs):
        return [], True
    def _store(self, *args, **kwargs):
        return []

@pytest.mark.django_db
def test_admin_bulk_approve_videos():
    v1 = Video.objects.create(title='Video 1', status=Video.STATUS_PENDING)
    v2 = Video.objects.create(title='Video 2', status=Video.STATUS_PENDING)

    rf = RequestFactory()
    request = rf.get('/')
    setattr(request, '_messages', DummyStorage(request))

    site = AdminSite()
    admin = VideoAdmin(Video, site)
    
    qs = Video.objects.filter(id__in=[v1.id, v2.id])
    approve_selected(admin, request=request, queryset=qs)

    v1.refresh_from_db()
    v2.refresh_from_db()
    assert v1.status == Video.STATUS_APPROVED
    assert v2.status == Video.STATUS_APPROVED

@pytest.mark.django_db
def test_admin_bulk_difficulty_and_content_type():
    v1 = Video.objects.create(title='Video 1', difficulty=Video.DIFFICULTY_EASY)
    site = AdminSite()
    admin = VideoAdmin(Video, site)

    qs = Video.objects.filter(id=v1.id)
    set_difficulty_hard(admin, request=None, queryset=qs)
    set_content_concept(admin, request=None, queryset=qs)

    v1.refresh_from_db()
    assert v1.difficulty == Video.DIFFICULTY_HARD
    assert v1.content_type == Video.CONTENT_TYPE_CONCEPT
