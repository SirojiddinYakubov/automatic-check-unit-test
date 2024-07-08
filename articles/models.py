from django.db import models
from django.contrib.auth import get_user_model

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
    description = models.TextField(blank=True, null=True)


class Article(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    content = models.TextField()
    thumbnail = models.ImageField(
        upload_to="articles/thumbnails/", blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT
    )
    topics = models.ManyToManyField(Topic, related_name="articles")
    views_count = models.IntegerField(default=0)


class Comment(BaseModel):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField()


class Favorite(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="favorites"
    )


class Clap(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="claps")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="claps")
    count = models.PositiveIntegerField(default=0)  # min:0, max:50


class Pin(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pins")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="pins")


class Follow(BaseModel):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )


class Recommendation(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendations"
    )
    more = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="more_recommended"
    )
    less = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="less_recommended"
    )


class Notification(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    read_at = models.DateTimeField(blank=True, null=True)


class ReadingHistory(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reading_history"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reading_history"
    )


class TopicFollow(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="topic_follows"
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="topic_follows"
    )


class Report(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports")
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="reports")


class FAQ(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
