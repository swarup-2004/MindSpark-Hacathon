# Generated by Django 5.1.1 on 2024-10-18 15:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_alter_useractivitylogs_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="sentiment",
            field=models.IntegerField(
                choices=[
                    (-1, "-1 - Negative"),
                    (0, "0 - Neutral"),
                    (1, "1 - Positive"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.IntegerField(
                choices=[
                    (1, "1 - Very Poor"),
                    (2, "2 - Poor"),
                    (3, "3 - Average"),
                    (4, "4 - Good"),
                    (5, "5 - Excellent"),
                ],
                default=3,
            ),
        ),
    ]