from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from phonics.management.commands.seed_external_games import WORDWALL_GAMES
from phonics.models import ExternalGame


class SeedExternalGamesCommandTests(TestCase):
    def run_command(self):
        output = StringIO()
        call_command("seed_external_games", stdout=output)
        return output.getvalue()

    def test_first_run_creates_one_approved_active_game_per_letter(self):
        output = self.run_command()

        self.assertIn("created=26", output)
        self.assertIn("updated=0", output)
        self.assertIn("unchanged=0", output)
        self.assertEqual(ExternalGame.objects.count(), 26)
        self.assertEqual(
            ExternalGame.objects.filter(
                is_active=True,
                review_status=ExternalGame.REVIEW_APPROVED,
            ).count(),
            26,
        )
        for letter, activity_url in WORDWALL_GAMES.items():
            game = ExternalGame.objects.get(letter=letter)
            self.assertEqual(game.title, f"Wordwall - {letter}")
            self.assertEqual(game.activity_url, activity_url)

    def test_second_run_is_idempotent_and_does_not_create_duplicates(self):
        self.run_command()
        output = self.run_command()

        self.assertIn("created=0", output)
        self.assertIn("updated=0", output)
        self.assertIn("unchanged=26", output)
        self.assertEqual(ExternalGame.objects.count(), 26)

    def test_existing_canonical_game_is_updated_in_place(self):
        game = ExternalGame.objects.create(
            letter="A",
            title="Old title",
            activity_url=WORDWALL_GAMES["A"],
            is_active=False,
            review_status=ExternalGame.REVIEW_PENDING,
        )

        output = self.run_command()
        game.refresh_from_db()

        self.assertIn("created=25", output)
        self.assertIn("updated=1", output)
        self.assertEqual(game.title, "Wordwall - A")
        self.assertTrue(game.is_active)
        self.assertEqual(game.review_status, ExternalGame.REVIEW_APPROVED)
        self.assertEqual(ExternalGame.objects.filter(letter="A").count(), 1)
