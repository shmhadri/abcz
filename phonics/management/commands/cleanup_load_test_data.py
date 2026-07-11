from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from phonics.management.commands.create_load_test_data import LOAD_TEST_EMAIL_DOMAIN


class Command(BaseCommand):
    help = "Safely delete load-test users created by create_load_test_data."

    def add_arguments(self, parser):
        parser.add_argument("--prefix", default="loadtest_user_", help="Safe username prefix.")
        parser.add_argument("--yes", action="store_true", help="Actually delete matching load-test users.")

    def handle(self, *args, **options):
        prefix = options["prefix"]
        if not prefix.startswith("loadtest_"):
            raise SystemExit("Refusing unsafe prefix. Prefix must start with 'loadtest_'.")

        User = get_user_model()
        queryset = User.objects.filter(
            username__startswith=prefix,
            email__endswith=f"@{LOAD_TEST_EMAIL_DOMAIN}",
        )
        count = queryset.count()

        if not options["yes"]:
            self.stdout.write(
                f"Dry run: {count} load-test users match prefix={prefix}. Re-run with --yes to delete."
            )
            return

        deleted, _ = queryset.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted load-test rows: users={count}, total_rows={deleted}"))
