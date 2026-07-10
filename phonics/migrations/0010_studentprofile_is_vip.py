from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("phonics", "0009_studentprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="is_vip",
            field=models.BooleanField(default=False, verbose_name="VIP user"),
        ),
    ]
