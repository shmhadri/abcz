from django.test import TestCase, override_settings
from django.urls import reverse

from phonics.tests import letters_asset_bundle as bundle


VIDEO_URLS = (
    "https://res.cloudinary.com/djkftm2cn/video/upload/v1787567647/Aa_zbifxy.mp4",
    "https://res.cloudinary.com/djkftm2cn/video/upload/v1787567647/Bb_keapwq.mp4",
    "https://res.cloudinary.com/djkftm2cn/video/upload/v1787568258/doc_2026-08-24_12-27-45_f9b45o.mp4",
)


@override_settings(DISABLE_AUTO_SEED=True)
class LetterVideoLessonTests(TestCase):
    def test_letters_page_includes_the_writing_video_controls(self):
        response = self.client.get(reverse("letters"))

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn('id="letterVideoBtn"', html)
        self.assertIn('id="letterVideoModal"', html)
        self.assertIn('id="letterVideoPlayer"', html)
        self.assertIn('controls playsinline preload="none"', html)
        self.assertIn("video_lessons.js", html)

    def test_video_url_is_assigned_only_inside_the_click_handler(self):
        source = bundle.read_text(bundle.LETTERS_JS_DIR / "video_lessons.js")

        for video_url in VIDEO_URLS:
            self.assertIn(video_url, source)
        self.assertIn("const VIDEO_LESSONS", source)
        self.assertIn("return VIDEO_LESSONS[letter] || null;", source)
        self.assertIn("button.hidden = !currentVideoLesson();", source)
        self.assertIn("title.textContent = lesson.title;", source)
        self.assertIn("player.src = lesson.url;", source)
        self.assertIn('player.pause();', source)
        self.assertIn('player.removeAttribute("src");', source)
        self.assertIn('player.load();', source)
        self.assertIn('event.key === "Escape"', source)

    def test_writing_video_button_hidden_state_overrides_the_general_button_style(self):
        stylesheet = bundle.read_text(bundle.LETTERS_CSS)

        self.assertIn(".letter-video-btn[hidden]", stylesheet)
        self.assertIn("display: none !important;", stylesheet)
        self.assertIn(".letter-info-btn", stylesheet)
        self.assertIn(".letter-reset-btn", stylesheet)

    def test_video_has_no_eager_html_source(self):
        response = self.client.get(reverse("letters"))
        html = response.content.decode("utf-8")

        video_markup = html.split('id="letterVideoPlayer"', 1)[1].split(">", 1)[0]
        self.assertNotIn("src=", video_markup)
