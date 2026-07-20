import uuid

from django.db import migrations, models


def populate_payment_idempotency_keys(apps, schema_editor):
    PaymentOrder = apps.get_model("phonics", "PaymentOrder")
    for order in PaymentOrder.objects.filter(idempotency_key__isnull=True).iterator():
        order.idempotency_key = uuid.uuid4()
        order.save(update_fields=["idempotency_key"])


class Migration(migrations.Migration):
    dependencies = [
        ("phonics", "0024_banktransferproof_bank_proof_status_created_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="canceled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="failed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="failure_code",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="failure_message",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="idempotency_key",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="moyasar_invoice_id",
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="moyasar_payment_id",
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder",
            name="payment_environment",
            field=models.CharField(
                choices=[("test", "Test"), ("live", "Live")],
                db_index=True,
                default="test",
                max_length=10,
            ),
        ),
        migrations.RunPython(populate_payment_idempotency_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="paymentorder",
            name="idempotency_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddConstraint(
            model_name="paymentorder",
            constraint=models.CheckConstraint(
                condition=models.Q(amount_halalas__gt=0),
                name="payment_amount_halalas_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="paymentorder",
            constraint=models.CheckConstraint(
                condition=~models.Q(provider="moyasar") | models.Q(currency="SAR"),
                name="moyasar_payment_currency_sar",
            ),
        ),
    ]
