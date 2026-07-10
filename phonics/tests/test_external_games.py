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

    def test_accepts_arabic_wordwall_resource_url(self):
        game = ExternalGame(
            letter="E",
            title="Arabic Wordwall E",
            activity_url="https://wordwall.net/ar/resource/22838490/letter-e",
        )

        game.full_clean()

    def test_accepts_www_arabic_wordwall_resource_url(self):
        game = ExternalGame(
            letter="E",
            title="Arabic Wordwall E",
            activity_url="https://www.wordwall.net/ar/resource/22838490/letter-e",
        )

        game.full_clean()

    def test_pending_games_route_is_blocked_in_level_one_policy(self):
        self.make_game(title="Pending A", review_status=ExternalGame.REVIEW_PENDING)

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Pending A", response.content.decode("utf-8"))

    def test_rejected_games_route_is_blocked_in_level_one_policy(self):
        self.make_game(title="Rejected A", review_status=ExternalGame.REVIEW_REJECTED)

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Rejected A", response.content.decode("utf-8"))

    def test_approved_games_route_is_blocked_in_level_one_policy(self):
        self.make_game(title="Approved A")
        self.make_game(
            title="Inactive Approved A",
            is_active=False,
            activity_url="https://wordwall.net/play/123/456",
        )

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 403)
        html = response.content.decode("utf-8")
        self.assertNotIn("Approved A", html)
        self.assertNotIn("goBackSafe", html)
        self.assertNotIn("wordwall-page", html)
        self.assertNotIn("noopener noreferrer", html)
        self.assertNotIn("Wordwall", html)
        self.assertNotIn("https://wordwall.net/resource/12345", html)
        self.assertNotIn("external-game-frame", html)
        self.assertNotIn("Inactive Approved A", html)

    def test_filtered_games_route_is_blocked_in_level_one_policy(self):
        self.make_game(title="Approved A", letter="A")
        self.make_game(
            title="Approved B",
            letter="B",
            activity_url="https://wordwall.net/resource/67890",
        )

        response = self.client.get("/letters/A/external-games/")

        self.assertEqual(response.status_code, 403)
        html = response.content.decode("utf-8")
        self.assertNotIn("Approved A", html)
        self.assertNotIn("Approved B", html)
