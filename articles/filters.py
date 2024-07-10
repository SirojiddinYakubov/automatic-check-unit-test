import django_filters
from .models import Article, Topic
from django.db.models import Count

class ArticleFilter(django_filters.FilterSet):
    top = django_filters.NumberFilter(method='filter_by_top')
    topic = django_filters.NumberFilter(method='filter_by_topic')
    is_recommend = django_filters.BooleanFilter(method='filter_by_recommend')

    class Meta:
        model = Article
        fields = ['top', 'is_recommend']

    def filter_by_top(self, queryset, name, value):
        if value:
            return queryset.order_by('-views_count')[:value]
        return queryset

    def filter_by_recommend(self, queryset, name, value):
        if value:
            user = self.request.user
            followed_topics = user.topic_follows.all().values_list('topic', flat=True)
            recommended_articles = queryset.filter(topics__in=followed_topics).distinct()
            return recommended_articles
        return queryset

    def filter_by_topic(self, queryset, name, value):
        return queryset.filter(topics__id=value)


class TopicFilter(django_filters.FilterSet):
    followed = django_filters.BooleanFilter(method='filter_by_followed')
    is_recommend = django_filters.BooleanFilter(method='filter_by_recommend')

    class Meta:
        model = Topic
        fields = ['followed', 'is_recommend']

    def filter_by_followed(self, queryset, name, value):
        queryset = Topic.objects.filter(topic_follows__user=self.request.user)
        return queryset

    def filter_by_recommend(self, queryset, name, value):
        queryset = Topic.objects.annotate(num_followers=Count('topic_follows')).order_by('-num_followers')[:5]
        return queryset
