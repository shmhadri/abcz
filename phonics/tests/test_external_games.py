from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from phonics.models import ExternalGame


@override_settings(DISABLE_AUTO_SEED=True)
class ExternalGameTests(TestCase):
    def make_game(self, **overrides):
        data = {
            "letter": "A",
            "title": "Approved A",
            "activity_url": "https://wordwall.net/resource/12345",
            "is_active": True,
            "review_status": ExternalGame.REVIEW_APPROVED,
        }
        data.update(overrides)
        return ExternalGame.objects.create(**data)

    def test_rejects_non_wordwall_url(self):
        game = ExternalGame(
            letter="A",
            title="Unsafe",
            activity_url="https://example.com/resource/123",
        )

        with self.assertRaises(ValidationError):
            game.full_clean()

    def test_pending_games_are_hidden_from_children(self):
        self.make_game(title="Pending A", review_status=ExternalGame.REVIEW_PENDING)

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pending A")

    def test_rejected_games_are_hidden_from_children(self):
        self.make_game(title="Rejected A", review_status=ExternalGame.REVIEW_REJECTED)

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Rejected A")

    def test_only_active_approved_games_are_visible(self):
        self.make_game(title="Approved A")
        self.make_game(
            title="Inactive Approved A",
            is_active=False,
            activity_url="https://wordwall.net/play/123/456",
        )

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved A")
        self.assertNotContains(response, "Inactive Approved A")

    def test_games_are_filtered_by_letter(self):
        self.make_game(title="Approved A", letter="A")
        self.make_game(
            title="Approved B",
            letter="B",
            activity_url="https://wordwall.net/resource/67890",
        )

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved A")
        self.assertNotContains(response, "Approved B")
