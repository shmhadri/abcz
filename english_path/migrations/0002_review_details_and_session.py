import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("english_path", "0001_initial")]
    operations = [
        migrations.AlterField(model_name="assessmentresult", name="level", field=models.CharField(blank=True, max_length=16)),
        migrations.AddField(model_name="reviewitem", name="difficulty", field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
        migrations.AddField(model_name="reviewitem", name="error_count", field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name="reviewitem", name="last_seen_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="reviewitem", name="subskill", field=models.CharField(default="general", max_length=64)),
        migrations.CreateModel(
            name="ReviewSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item_ids", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="english_review_sessions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
