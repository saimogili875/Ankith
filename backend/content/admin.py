from django.contrib import admin
from .models import Chapter, Topic, Playlist, Video, LiveSession

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_order', 'topic_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TopicInline]

    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'chapter', 'slug', 'sort_order')
    list_filter = ('chapter',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_playlist_id', 'item_count')
    search_fields = ('title', 'youtube_playlist_id')


@admin.action(description='Approve selected videos')
def approve_selected(modeladmin, request, queryset):
    updated = queryset.update(status=Video.STATUS_APPROVED)
    modeladmin.message_user(request, f"{updated} video(s) successfully marked as approved.")

@admin.action(description='Set difficulty to Easy')
def set_difficulty_easy(modeladmin, request, queryset):
    queryset.update(difficulty=Video.DIFFICULTY_EASY)

@admin.action(description='Set difficulty to Medium')
def set_difficulty_medium(modeladmin, request, queryset):
    queryset.update(difficulty=Video.DIFFICULTY_MEDIUM)

@admin.action(description='Set difficulty to Hard')
def set_difficulty_hard(modeladmin, request, queryset):
    queryset.update(difficulty=Video.DIFFICULTY_HARD)

@admin.action(description='Set difficulty to Advanced')
def set_difficulty_advanced(modeladmin, request, queryset):
    queryset.update(difficulty=Video.DIFFICULTY_ADVANCED)

@admin.action(description='Set content type to Concept')
def set_content_concept(modeladmin, request, queryset):
    queryset.update(content_type=Video.CONTENT_TYPE_CONCEPT)

@admin.action(description='Set content type to PYQ')
def set_content_pyq(modeladmin, request, queryset):
    queryset.update(content_type=Video.CONTENT_TYPE_PYQ)

@admin.action(description='Set content type to Problem Solving')
def set_content_problem_solving(modeladmin, request, queryset):
    queryset.update(content_type=Video.CONTENT_TYPE_PROBLEM_SOLVING)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'source', 'status', 'content_type', 'difficulty',
        'chapter', 'topic', 'is_short', 'duration_sec', 'published_at'
    )
    list_editable = ('status', 'difficulty', 'content_type')
    list_filter = (
        'status', 'source', 'content_type', 'difficulty',
        'is_short', 'pyq_year', 'chapter', 'topic'
    )
    search_fields = ('title', 'description', 'youtube_id', 'bunny_video_id')
    raw_id_fields = ('chapter', 'topic', 'playlist')
    actions = [
        approve_selected,
        set_difficulty_easy,
        set_difficulty_medium,
        set_difficulty_hard,
        set_difficulty_advanced,
        set_content_concept,
        set_content_pyq,
        set_content_problem_solving,
    ]


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'scheduled_time', 'status', 'source', 'recording_link')
    list_filter = ('status', 'source')
    search_fields = ('title', 'stream_id')
    raw_id_fields = ('recording_link',)
