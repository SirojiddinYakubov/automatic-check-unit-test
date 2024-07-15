from django.contrib import admin
from .models import (
    Topic, Article,
    Comment, Favorite, Clap,
    Pin, Follow, Recommendation,
    Notification, ReadingHistory,
    TopicFollow, FAQ, Report,)

class ArticlesAdmin(admin.ModelAdmin):
    def get_topics(self, obj):
        return ", ".join([topic.name for topic in obj.topics.all()])

    list_display = ('title', 'author', 'get_topics',)


admin.site.register(Topic)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(Comment)
admin.site.register(Favorite)
admin.site.register(Clap)
admin.site.register(Pin)
admin.site.register(Follow)
admin.site.register(Recommendation)
admin.site.register(Notification)
admin.site.register(ReadingHistory)
admin.site.register(TopicFollow)
admin.site.register(FAQ)
admin.site.register(Report)
