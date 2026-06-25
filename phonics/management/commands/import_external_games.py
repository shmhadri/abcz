import csv

from django.core.management.base import BaseCommand, CommandError

from phonics.models import ExternalGame


class Command(BaseCommand):
    help = "Import external Wordwall games from a CSV file with columns: letter,title,url,notes"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Path to CSV file with letter,title,url,notes columns")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        created_count = 0
        skipped_count = 0

        try:
            csv_file = open(csv_path, newline="", encoding="utf-8-sig")
        except OSError as exc:
            raise CommandError(f"Could not open CSV file: {exc}") from exc

        with csv_file:
            reader = csv.DictReader(csv_file)
            required_headers = {"letter", "title", "url", "notes"}
            missing_headers = required_headers - set(reader.fieldnames or [])
            if missing_headers:
                raise CommandError(f"Missing CSV columns: {', '.join(sorted(missing_headers))}")

            for row_number, row in enumerate(reader, start=2):
                game = ExternalGame(
                    letter=(row.get("letter") or "").strip().upper(),
                    title=(row.get("title") or "").strip(),
                    activity_url=(row.get("url") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                    review_status=ExternalGame.REVIEW_PENDING,
                    is_active=True,
                )

                try:
                    game.full_clean()
                    game.save()
                except Exception as exc:
                    skipped_count += 1
                    self.stderr.write(f"Skipped row {row_number}: {exc}")
                    continue

                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created_count} external games as pending. Skipped {skipped_count} rows."
            )
        )
