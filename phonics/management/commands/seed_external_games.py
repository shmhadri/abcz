from django.core.management.base import BaseCommand

from phonics.models import ExternalGame


WORDWALL_GAMES = {
    "A": "https://wordwall.net/resource/115480095/a",
    "B": "https://wordwall.net/ar/resource/115487290",
    "C": "https://wordwall.net/ar/resource/115487526",
    "D": "https://wordwall.net/ar/resource/115487791",
    "E": "https://wordwall.net/ar/resource/115858875",
    "F": "https://wordwall.net/ar/resource/115699978",
    "G": "https://wordwall.net/ar/resource/115558466",
    "H": "https://wordwall.net/ar/resource/115558592",
    "I": "https://wordwall.net/ar/resource/115558709",
    "J": "https://wordwall.net/ar/resource/115558804",
    "K": "https://wordwall.net/ar/resource/115558886",
    "L": "https://wordwall.net/ar/resource/115558915",
    "M": "https://wordwall.net/ar/resource/115558925",
    "N": "https://wordwall.net/ar/resource/115558946",
    "O": "https://wordwall.net/ar/resource/115558952",
    "P": "https://wordwall.net/ar/resource/115558974",
    "Q": "https://wordwall.net/ar/resource/115558990",
    "R": "https://wordwall.net/ar/resource/115700801",
    "S": "https://wordwall.net/ar/resource/115559019",
    "T": "https://wordwall.net/ar/resource/115559040",
    "U": "https://wordwall.net/ar/resource/115559051",
    "V": "https://wordwall.net/ar/resource/115559064",
    "W": "https://wordwall.net/ar/resource/115559070",
    "X": "https://wordwall.net/ar/resource/115701577",
    "Y": "https://wordwall.net/ar/resource/115559091",
    "Z": "https://wordwall.net/ar/resource/115559107",
}


class Command(BaseCommand):
    help = "Create or update the approved Wordwall game for each letter A-Z."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        unchanged_count = 0

        for letter, activity_url in WORDWALL_GAMES.items():
            defaults = {
                "letter": letter,
                "title": f"Wordwall - {letter}",
                "activity_url": activity_url,
                "is_active": True,
                "review_status": ExternalGame.REVIEW_APPROVED,
            }
            # Match the canonical URL first.  ``first`` also lets the command run
            # safely on installations that already contain duplicate legacy rows;
            # it updates one canonical record and never deletes user data.
            existing = (
                ExternalGame.objects.filter(letter=letter, activity_url=activity_url)
                .order_by("id")
                .first()
            )
            if existing is None:
                game, created = ExternalGame.objects.update_or_create(
                    letter=letter,
                    activity_url=activity_url,
                    defaults=defaults,
                )
            else:
                before = {field: getattr(existing, field) for field in defaults}
                game, created = ExternalGame.objects.update_or_create(
                    pk=existing.pk,
                    defaults=defaults,
                )

            if created:
                created_count += 1
            elif existing is not None and before == defaults:
                unchanged_count += 1
            else:
                updated_count += 1

        total = len(WORDWALL_GAMES)
        self.stdout.write(
            self.style.SUCCESS(
                f"Wordwall seed complete: created={created_count} "
                f"updated={updated_count} unchanged={unchanged_count} total={total}"
            )
        )
