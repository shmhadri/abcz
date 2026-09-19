from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("phonics", "0031_banktransferactivationcode"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="tiktok_purchase_claimed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
