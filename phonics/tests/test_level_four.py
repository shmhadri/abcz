from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import EnglishFoundationProgress, StudentProfile
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class LevelFourTests(TestCase):
    section_paths = [
        "/level-four/reading/",
        "/level-four/listening/",
        "/level-four/speaking/",
        "/level-four/writing/",
        "/level-four/stories/",
        "/level-four/exam/",
        "/level-four/worksheets/",
    ]

    worksheet_paths = [
        "/level-four/worksheets/reading/",
        "/level-four/worksheets/listening/",
        "/level-four/worksheets/speaking/",
        "/level-four/worksheets/writing/",
        "/level-four/worksheets/stories/",
        "/level-four/worksheets/exam-review/",
    ]

    def setUp(self):
        self.user = User.objects.create_user(username="level-four-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_level_four_overview_is_short_dashboard(self):
        response = self.client.get("/level-four/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "المستوى الرابع")
        self.assertContains(response, "Reading & Real English")
        self.assertContains(response, "Reading Passages")
        self.assertContains(response, "Listening Practice")
        self.assertContains(response, "Speaking Missions")
        self.assertContains(response, "Writing Practice")
        self.assertContains(response, "Story Mode")
        self.assertContains(response, "Level 4 Exam")
        self.assertContains(response, "أوراق عمل المستوى الرابع")
        self.assertNotContains(response, "Every morning, I wake up")
        self.assertNotContains(response, "School Morning")
        self.assertLessEqual(response.content.decode("utf-8").count("Level 4 Exam"), 2)

    def test_level_four_reading_page(self):
        response = self.client.get("/level-four/reading/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reading Passages")
        self.assertContains(response, "My School Day")
        self.assertContains(response, "level_four_reading")

    def test_level_four_theme_defaults_to_light_and_has_toggle(self):
        response = self.client.get("/level-four/")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertContains(response, "الوضع الليلي")
        self.assertContains(response, 'data-level-four-theme-toggle', html=False)
        self.assertNotIn('class="level-four-page dark"', html)
        self.assertNotIn('data-theme="dark"', html)

    def test_level_four_section_pages_have_back_button_and_theme_toggle(self):
        for path in self.section_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "رجوع للمستوى الرابع")
                self.assertContains(response, "الوضع الليلي")
                self.assertContains(response, 'data-level-four-theme-toggle', html=False)

    def test_level_four_worksheet_pages_have_two_back_buttons_and_theme_toggle(self):
        for path in self.worksheet_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "رجوع للمستوى الرابع")
                self.assertContains(response, "رجوع لأوراق العمل")
                self.assertContains(response, "الوضع الليلي")

    def test_level_four_listening_page(self):
        response = self.client.get("/level-four/listening/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Listening Practice")
        self.assertContains(response, "School Morning")
        self.assertContains(response, "level_four_listening")

    def test_level_four_speaking_page(self):
        response = self.client.get("/level-four/speaking/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Speaking Missions")
        self.assertContains(response, "Introduce Yourself")
        self.assertContains(response, "Role Play Mini")
        self.assertContains(response, "level_four_speaking")

    def test_level_four_writing_page(self):
        response = self.client.get("/level-four/writing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Writing Practice")
        self.assertContains(response, "Write About Yourself")
        self.assertContains(response, "مساعد بناء الجملة")
        self.assertContains(response, "level_four_writing")

    def test_level_four_stories_page(self):
        response = self.client.get("/level-four/stories/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Story Mode")
        self.assertContains(response, "The Lost Bag")
        self.assertContains(response, "level_four_stories")

    def test_level_four_exam_page(self):
        response = self.client.get("/level-four/exam/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Level 4 Exam")
        self.assertContains(response, "اختبار المستوى الرابع")
        self.assertContains(response, "ابدأ الاختبار")
        self.assertContains(response, "شهادة إتقان المستوى الرابع")
        self.assertContains(response, "level_four_exam")

    def test_level_four_worksheets_hub(self):
        response = self.client.get("/level-four/worksheets/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أوراق عمل المستوى الرابع")
        self.assertContains(response, "Reading Worksheet")
        self.assertContains(response, "Listening Worksheet")
        self.assertContains(response, "Exam Review Worksheet")

    def test_level_four_worksheet_pages_return_success(self):
        for path in [
            "/level-four/worksheets/reading/",
            "/level-four/worksheets/listening/",
            "/level-four/worksheets/speaking/",
            "/level-four/worksheets/writing/",
            "/level-four/worksheets/stories/",
            "/level-four/worksheets/exam-review/",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Level 4 Worksheet")
                self.assertContains(response, "طباعة الورقة")

    def test_home_has_level_four_buttons_in_header_and_menu(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertEqual(html.count('href="/level-four/"'), 2)
        self.assertIn('data-learning-level="4"', html)
        self.assertIn('data-menu-learning-level="4"', html)
        self.assertContains(response, 'href="/level-four/"', html=False)

    def test_level_four_css_contains_theme_responsive_touch_and_print_rules(self):
        css = Path("static/css/level_four.css").read_text(encoding="utf-8")

        self.assertIn("@media print", css)
        self.assertIn("@media (max-width", css)
        self.assertIn("body.dark", css)
        self.assertIn('[data-theme="dark"]', css)
        self.assertNotIn("prefers-color-scheme", css)
        self.assertIn("level-four-toolbar", css)
        self.assertIn("level-four-theme-toggle", css)
        self.assertIn("level-four-back-link", css)
        self.assertIn("min-height: 44px", css)
        self.assertIn("touch-action", css)

    def test_level_four_js_contains_theme_controls(self):
        script = Path("static/js/level_four.js").read_text(encoding="utf-8")

        self.assertIn("level_four_theme", script)
        self.assertIn("initLevelFourTheme", script)
        self.assertIn("toggleLevelFourTheme", script)

    def assert_progress_section_is_accepted(self, section, activity_type, points):
        user = User.objects.create_user(username=f"{section}-user", password="pass12345")
        StudentProfile.objects.create(user=user, student_name=section, grade="Grade 4")
        grant_active_subscription(user, "diamond")
        self.client.force_login(user)

        response = self.client.post(
            "/api/english-foundation/progress/",
            data=f'{{"section":"{section}","activity_type":"{activity_type}","points":{points}}}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["section"], section)
        self.assertTrue(
            EnglishFoundationProgress.objects.filter(
                user=user,
                section=section,
                points=points,
            ).exists()
        )

    def test_level_four_progress_sections_are_accepted(self):
        for section, activity_type, points in [
            ("level_four_reading", "speed", 10),
            ("level_four_listening", "quick_quiz", 20),
            ("level_four_speaking", "speaking_challenge", 25),
            ("level_four_writing", "writing_challenge", 25),
            ("level_four_stories", "story_challenge", 25),
            ("level_four_exam", "finish_exam", 50),
        ]:
            with self.subTest(section=section):
                self.assert_progress_section_is_accepted(section, activity_type, points)
