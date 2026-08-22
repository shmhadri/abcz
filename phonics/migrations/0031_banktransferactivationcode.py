# Generated manually to keep the deployment schema explicit.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("phonics", "0030_adminauditlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankTransferActivationCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code_hash", models.CharField(editable=False, max_length=255)),
                ("expires_at", models.DateTimeField()),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("issued_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="issued_bank_transfer_activation_codes", to=settings.AUTH_USER_MODEL)),
                ("payment_order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="bank_transfer_activation_code", to="phonics.paymentorder")),
            ],
            options={"ordering": ["-issued_at"]},
        ),
        migrations.AddIndex(
            model_name="banktransferactivationcode",
            index=models.Index(fields=["expires_at", "used_at"], name="phonics_ban_expires_74370f_idx"),
        ),
    ]
