from django.test import TestCase, override_settings


@override_settings(DISABLE_AUTO_SEED=True)
class GamesCenterTests(TestCase):
    def test_games_center_returns_success(self):
        response = self.client.get("/games/")

        self.assertEqual(response.status_code, 200)

    def test_games_center_contains_required_content(self):
        response = self.client.get("/games/")

        self.assertContains(response, "الألعاب والتدريبات")
        self.assertContains(response, "Games & Interactive Training")
        self.assertContains(response, "Flashcards")
        self.assertContains(response, "Sentence Builder")
        self.assertContains(response, "Speak Challenge")
        self.assertContains(response, "One Minute Challenge")
        self.assertContains(response, "تحدي اليوم")

    def test_legacy_english_games_uses_games_center(self):
        response = self.client.get("/english-games/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Games & Interactive Training")
