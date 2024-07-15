# Generated by Django 5.0.4 on 2024-07-15 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0010_article_reads_count"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recommendation",
            name="less",
        ),
        migrations.RemoveField(
            model_name="recommendation",
            name="more",
        ),
        migrations.AddField(
            model_name="recommendation",
            name="less",
            field=models.ManyToManyField(
                limit_choices_to={"is_active": True},
                related_name="less_recommended",
                to="articles.topic",
            ),
        ),
        migrations.AddField(
            model_name="recommendation",
            name="more",
            field=models.ManyToManyField(
                limit_choices_to={"is_active": True},
                related_name="more_recommended",
                to="articles.topic",
            ),
        ),
    ]
