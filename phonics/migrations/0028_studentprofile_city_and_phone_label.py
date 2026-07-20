from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("phonics", "0027_subscription_commerce_policy"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="city",
            field=models.CharField(blank=True, max_length=100, verbose_name="المدينة"),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="parent_phone",
            field=models.CharField(blank=True, max_length=30, verbose_name="رقم الجوال"),
        ),
    ]
