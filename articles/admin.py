from django.contrib import admin
from .models import (
    Topic, Article, Comment, Favorite, Clap, Pin, Follow,
    Recommendation, Notification, ReadingHistory, TopicFollow,
    FAQ, Report
)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active',)
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Article)
class ArticlesAdmin(admin.ModelAdmin):
    def get_topics(self, obj):
        return ", ".join([topic.name for topic in obj.topics.all()])

    list_display = ('id', 'title', 'status', 'author', 'get_topics',)
    list_display_links = ('title',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'user', 'content',)
    list_display_links = ('id', 'article',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article', 'created_at')
    list_display_links = ('id', 'user',)

@admin.register(Clap)
class ClapAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article', 'count',)
    list_display_links = ('id', 'user',)

@admin.register(Pin)
class PinAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article',)
    list_display_links = ('id', 'user',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followee',)
    list_display_links = ('id', 'follower',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_display_links = ('id', 'user',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'read_at',)
    list_display_links = ('id', 'user',)

@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article',)
    list_display_links = ('id', 'user',)

@admin.register(TopicFollow)
class TopicFollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic',)
    list_display_links = ('id', 'user',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'article',)
    list_display_links = ('id', 'article',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question',)
    list_display_links = ('id', 'question',)
