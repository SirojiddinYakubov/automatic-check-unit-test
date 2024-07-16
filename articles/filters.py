import django_filters
from .models import Article, Topic, Recommendation
from django.db.models import Q
from django.db.models import Count

class ArticleFilter(django_filters.FilterSet):
    top = django_filters.NumberFilter(method='filter_by_top')
    topic = django_filters.NumberFilter(method='filter_by_topic')
    is_recommend = django_filters.BooleanFilter(method='filter_by_recommend')

    class Meta:
        model = Article
        fields = ['top', 'topic', 'is_recommend']

    def filter_by_top(self, queryset, name, value):
        if value:
            return queryset.order_by('-views_count')[:value]
        return queryset

    def filter_by_recommend(self, queryset, name, value):
        user = self.request.user
        if value:
            recommendations = Recommendation.objects.filter(user=user)
            more_topics = recommendations.values_list('more', flat=True)
            less_topics = recommendations.values_list('less', flat=True)

            followed_topics = user.followed_topics.values_list('id', flat=True)

            if more_topics.exists() or followed_topics.exists():
                queryset = queryset.filter(Q(topics__in=more_topics) | Q(topics__in=followed_topics))

            if less_topics.exists():
                queryset = queryset.exclude(topics__in=less_topics)
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


class SearchFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        model = Article
        fields = []

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(summary__icontains=value) |
            Q(content__icontains=value) |
            Q(topics__name__icontains=value) |
            Q(topics__description__icontains=value)
        ).distinct()
