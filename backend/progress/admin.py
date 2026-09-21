from django.contrib import admin
from .models import Bookmark, WatchHistory

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    search_fields = ('user__username', 'user__email', 'video__title')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'video')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'seconds_watched', 'completed', 'updated_at')
    search_fields = ('user__username', 'user__email', 'video__title')
    list_filter = ('completed', 'updated_at')
    raw_id_fields = ('user', 'video')
