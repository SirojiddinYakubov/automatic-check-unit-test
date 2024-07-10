from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from django.core import validators
from django.db.models import Sum
from django.db.models import UniqueConstraint

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArticleStatus(models.TextChoices):
    DRAFT = "draft", "Editing article"
    PENDING = "pending", "Pending"
    PUBLISH = "publish", "Publish"
    PRIVATE = "private", "Private"
    TRASH = "trash", "Trash"
    ARCHIVE = "archive", "Archive"


class Topic(BaseModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "topic"
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(BaseModel):
    author = models.ForeignKey(User, limit_choices_to={
                               'is_active': True}, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    content = RichTextField()
    thumbnail = models.ImageField(
        upload_to="articles/thumbnails/", blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT
    )
    topics = models.ManyToManyField(Topic, limit_choices_to={
                                    'is_active': True}, related_name="articles")
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "article"
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def claps_count(self):
        total_claps = self.claps.aggregate(
            total_claps=Sum('count'))['total_claps']
        return total_claps or 0


class Comment(BaseModel):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, limit_choices_to={
                             'is_active': True}, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = RichTextField()

    class Meta:
        db_table = "comment"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.article}"


class Favorite(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="favorites")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        db_table = "favorite"
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        ordering = ['-created_at']


class Clap(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="claps")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="claps")
    count = models.PositiveIntegerField(
        default=0,
        validators=[
            validators.MaxValueValidator(50)
        ])

    class Meta:
        db_table = "clap"
        verbose_name = "Clap"
        verbose_name_plural = "Claps"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.count}"


class Pin(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="pins")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="pins")

    class Meta:
        db_table = "pin"
        verbose_name = "Pin"
        verbose_name_plural = "Pins"
        ordering = ['-created_at']


class Follow(BaseModel):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="following"
    )
    followee = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="followers"
    )

    class Meta:
        db_table = "follow"
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        ordering = ['-created_at']


class Recommendation(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="recommendations"
    )
    more = models.ForeignKey(
        Topic, limit_choices_to={'is_active': True}, on_delete=models.CASCADE, related_name="more_recommended"
    )
    less = models.ForeignKey(
        Topic, limit_choices_to={'is_active': True}, on_delete=models.CASCADE, related_name="less_recommended", null=True, blank=True
    )

    class Meta:
        db_table = "recommendation"
        verbose_name = "Recommendation"
        verbose_name_plural = "Recommendations"
        ordering = ['-created_at']


class Notification(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="notifications"
    )
    message = models.TextField()
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "notification"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']


class ReadingHistory(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="reading_history"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reading_history"
    )

    class Meta:
        db_table = "reading_history"
        verbose_name = "Reading History"
        verbose_name_plural = "Reading Histories"
        ordering = ['-created_at']


class TopicFollow(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="topic_follows"
    )
    topic = models.ForeignKey(
        Topic, limit_choices_to={'is_active': True}, on_delete=models.CASCADE, related_name="topic_follows"
    )

    class Meta:
        db_table = "topic_follow"
        verbose_name = "Topic Follow"
        verbose_name_plural = "Topic Follows"
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(fields=['user', 'topic'],
                             name='unique_user_topic')
        ]

    def __str__(self):
        return f"{self.user.username} follows {self.topic.name}"


class Report(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="reports")
    topic = models.ForeignKey(
        Topic, limit_choices_to={'is_active': True}, on_delete=models.CASCADE, related_name="reports")

    class Meta:
        db_table = "report"
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']


class FAQ(BaseModel):
    question = models.CharField(max_length=255)
    answer = RichTextField()

    class Meta:
        db_table = "faq"
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['question']

    def __str__(self):
        return self.question
