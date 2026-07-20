from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.tests.subscription_helpers import grant_active_subscription

from phonics.views import (
    FOUNDATION_VOCABULARY_CATEGORIES,
    LEVEL_TWO_GRAMMAR_LESSONS,
    SOUND_PATTERN_ACTIVITIES,
    SOUND_PATTERN_GROUPS,
    foundation_vocabulary_total_words,
    sound_pattern_total_units,
)


@override_settings(DISABLE_AUTO_SEED=True)
class SoundsPatternsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sounds-silver", password="StrongPass123!")
        grant_active_subscription(self.user, "silver")
        self.client.force_login(self.user)

    def test_sound_patterns_cover_required_groups(self):
        groups = {group["id"]: group for group in SOUND_PATTERN_GROUPS}

        self.assertIn("digraphs", groups)
        self.assertIn("ending_sounds", groups)
        self.assertIn("trigraphs", groups)
        self.assertIn("advanced_patterns", groups)
        self.assertTrue(groups["advanced_patterns"].get("locked"))
        self.assertGreaterEqual(sound_pattern_total_units(), 20)

    def test_sound_patterns_include_required_level_two_content(self):
        groups = {group["id"]: group for group in SOUND_PATTERN_GROUPS}
        patterns_for = lambda group_id: {item["pattern"] for item in groups[group_id]["patterns"]}

        self.assertSetEqual(patterns_for("digraphs"), {"sh", "ch", "th", "ph", "wh", "ck"})
        self.assertSetEqual(patterns_for("ending_sounds"), {"ck", "ng", "nk", "ll", "ss", "ff", "zz"})
        self.assertSetEqual(patterns_for("trigraphs"), {"tch", "dge", "str", "spr", "spl", "shr"})
        self.assertTrue({"tion", "ture", "sion", "ssion", "ough"}.issubset(patterns_for("advanced_patterns")))
        self.assertIn("augh", patterns_for("advanced_patterns"))
        self.assertTrue(all(item["examples"] for item in groups["advanced_patterns"]["patterns"]))

    def test_sounds_page_exposes_pattern_data_and_tab(self):
        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="soundPatternsData"')
        self.assertContains(response, 'id="soundPatternActivitiesData"')
        self.assertContains(response, 'data-tab="digraphs"')
        self.assertContains(response, 'data-tab="ending-sounds"')
        self.assertContains(response, 'data-tab="trigraphs"')
        self.assertContains(response, 'data-tab="advanced-patterns"')
        self.assertContains(response, 'id="digraphGroups"')
        self.assertContains(response, 'id="digraphFinalQuiz"')
        self.assertContains(response, 'id="digraphCertificate"')
        self.assertContains(response, 'id="digraphProgressFill"')
        self.assertContains(response, 'id="endingGroups"')
        self.assertContains(response, 'id="trigraphGroups"')
        self.assertContains(response, 'id="trigraphFinalQuiz"')
        self.assertContains(response, 'id="trigraphCertificate"')
        self.assertContains(response, 'id="trigraphProgressFill"')
        self.assertContains(response, 'id="advancedGroups"')
        self.assertContains(response, 'id="advancedActivities"')
        self.assertContains(response, 'id="advancedProgressFill"')

    def test_foundation_vocabulary_data_covers_required_categories(self):
        categories = {category["id"]: category for category in FOUNDATION_VOCABULARY_CATEGORIES}

        self.assertSetEqual(
            set(categories),
            {"colors", "animals", "family", "feelings", "daily-verbs", "foods", "drinks", "numbers", "calendar"},
        )
        self.assertGreaterEqual(foundation_vocabulary_total_words(), 80)
        self.assertEqual(categories["colors"]["words"][0]["word"], "red")
        self.assertEqual(categories["colors"]["words"][0]["arabic"], "أحمر")
        self.assertEqual(categories["animals"]["words"][0]["word"], "cat")
        self.assertEqual(categories["animals"]["words"][0]["arabic"], "قط")
        self.assertEqual(len(categories["animals"]["words"]), 31)
        self.assertEqual(
            {group["title_en"] for group in categories["animals"]["groups"]},
            {"Pets", "Farm Animals", "Wild Animals", "Sea Animals", "Insects & Small Creatures"},
        )
        self.assertTrue(all(word["group_en"] and word["habitat"] for word in categories["animals"]["words"]))
        self.assertEqual(len(categories["foods"]["words"]), 40)
        self.assertEqual(
            {group["title_en"] for group in categories["foods"]["groups"]},
            {"Fruits", "Vegetables", "Daily Meals", "Snacks", "Sweets", "Healthy Food"},
        )
        self.assertTrue(all(word["group_en"] and word["food_type"] for word in categories["foods"]["words"]))
        self.assertEqual(len(categories["calendar"]["words"]), 19)
        self.assertEqual(
            {group["title_en"] for group in categories["calendar"]["groups"]},
            {"Days", "Months"},
        )
        self.assertTrue(all(word["group_en"] and word["time_type"] for word in categories["calendar"]["words"]))
        self.assertTrue(all(word["arabic"] and word["icon"] for category in FOUNDATION_VOCABULARY_CATEGORIES for word in category["words"]))

    def test_sounds_page_exposes_foundation_vocabulary_section(self):
        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مفردات التأسيس")
        self.assertContains(response, "Foundation Vocabulary")
        self.assertContains(response, 'id="foundationVocabularyData"', html=False)
        self.assertContains(response, 'data-tab="foundation-vocabulary"', html=False)
        self.assertContains(response, 'id="vocabCategoryGrid"', html=False)
        self.assertContains(response, 'id="vocabWordGrid"', html=False)
        self.assertContains(response, 'data-vocab-listen', html=False)
        self.assertContains(response, 'data-vocab-mic', html=False)
        self.assertContains(response, "الألوان")
        self.assertContains(response, "الحيوانات")
        self.assertContains(response, "العائلة")
        self.assertContains(response, "المشاعر")
        self.assertContains(response, "الأفعال اليومية")
        self.assertContains(response, "الأطعمة")
        self.assertContains(response, "المشروبات")
        self.assertContains(response, "الأرقام")
        self.assertContains(response, "الأيام والأشهر")
        self.assertContains(response, "red")
        self.assertContains(response, "أحمر")
        self.assertContains(response, "cat")
        self.assertContains(response, "قط")
        self.assertContains(response, "family")

    def test_animals_vocabulary_category_is_enhanced(self):
        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Animals")
        self.assertContains(response, "Pets")
        self.assertContains(response, "Farm Animals")
        self.assertContains(response, "Wild Animals")
        self.assertContains(response, "Sea Animals")
        self.assertContains(response, "Small Creatures")
        self.assertContains(response, "dolphin")
        self.assertContains(response, "bee")
        self.assertContains(response, "Animal Mini Story")
        self.assertContains(response, "data-animal-group", html=False)
        self.assertContains(response, "data-animal-story-answer", html=False)
        self.assertContains(response, "mastered_animals")
        self.assertContains(response, "animal_quiz_score")
        self.assertContains(response, "animal_mic_success")
        self.assertContains(response, "SpeechService.startRecognition", html=False)

    def test_foods_vocabulary_category_is_enhanced(self):
        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Foods")
        self.assertContains(response, "Fruits")
        self.assertContains(response, "Vegetables")
        self.assertContains(response, "Daily Meals")
        self.assertContains(response, "Snacks")
        self.assertContains(response, "Sweets")
        self.assertContains(response, "Healthy Food")
        self.assertContains(response, "apple")
        self.assertContains(response, "carrot")
        self.assertContains(response, "bread")
        self.assertContains(response, "cake")
        self.assertContains(response, "Food Mini Story")
        self.assertContains(response, "data-food-group", html=False)
        self.assertContains(response, "data-food-story-answer", html=False)
        self.assertContains(response, "mastered_foods")
        self.assertContains(response, "food_quiz_score")
        self.assertContains(response, "food_mic_success")
        self.assertContains(response, "SpeechService.startRecognition", html=False)

    def test_calendar_vocabulary_category_is_enhanced(self):
        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Days & Months")
        self.assertContains(response, "Days")
        self.assertContains(response, "Months")
        self.assertContains(response, "Monday")
        self.assertContains(response, "Friday")
        self.assertContains(response, "January")
        self.assertContains(response, "December")
        self.assertContains(response, "Calendar Mini Story")
        self.assertContains(response, "data-calendar-group", html=False)
        self.assertContains(response, "data-calendar-story-answer", html=False)
        self.assertContains(response, "mastered_calendar")
        self.assertContains(response, "calendar_quiz_score")
        self.assertContains(response, "calendar_mic_success")
        self.assertContains(response, "SpeechService.startRecognition", html=False)

    def test_level_two_grammar_lessons_are_available_in_sounds(self):
        lessons = {lesson["id"]: lesson for lesson in LEVEL_TWO_GRAMMAR_LESSONS}

        self.assertSetEqual(set(lessons), {"demonstratives", "pronouns", "possessive-nouns"})
        self.assertTrue(all(lesson["activities"] for lesson in lessons.values()))
        self.assertTrue(all(lesson["groups"] for lesson in lessons.values()))
        self.assertIn("this", [item["term"] for group in lessons["demonstratives"]["groups"] for item in group["entries"]])
        self.assertIn("I", [item["term"] for group in lessons["pronouns"]["groups"] for item in group["entries"]])
        self.assertIn("Ali's bag", [item["term"] for group in lessons["possessive-nouns"]["groups"] for item in group["entries"]])

        response = self.client.get("/sounds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="levelTwoGrammarData"', html=False)
        self.assertContains(response, 'data-tab="foundation-grammar"', html=False)
        self.assertContains(response, "قواعد المستوى الثاني")
        self.assertContains(response, "Demonstratives")
        self.assertContains(response, "Pronouns")
        self.assertContains(response, "Possessive Nouns")
        self.assertContains(response, "This is my pen.")
        self.assertContains(response, "She reads books.")
        self.assertContains(response, "Ali's bag is blue.")
        self.assertContains(response, "data-grammar-mic", html=False)
        self.assertContains(response, "abcz-level-two-grammar-progress-v1")
        self.assertContains(response, "SpeechService.startRecognition", html=False)

    def test_pattern_activities_include_listen_and_mic_practice(self):
        self.assertTrue(any(activity.get("listen") for activity in SOUND_PATTERN_ACTIVITIES))
        self.assertTrue(any(activity.get("mic") for activity in SOUND_PATTERN_ACTIVITIES))
        self.assertTrue(any(activity.get("mode") == "drag" for activity in SOUND_PATTERN_ACTIVITIES))
        activity_ids = {activity["id"] for activity in SOUND_PATTERN_ACTIVITIES}
        self.assertIn("digraph_complete_ship", activity_ids)
        self.assertIn("digraph_sort_words", activity_ids)
        self.assertIn("digraph_odd_one", activity_ids)
        self.assertIn("trigraph_complete_catch", activity_ids)
        self.assertIn("trigraph_sort_words", activity_ids)
        self.assertIn("trigraph_odd_one", activity_ids)
        self.assertIn("advanced_pattern_match", activity_ids)
        self.assertIn("advanced_sort_by_ending", activity_ids)
        self.assertIn("advanced_word_detective", activity_ids)

    def test_sounds_worksheet_exposes_level_two_sheets(self):
        expected_sheets = [
            "digraphs",
            "digraph-sh",
            "digraph-ch",
            "digraph-th",
            "digraph-review",
            "ending-sounds",
            "trigraphs",
            "tch",
            "dge",
            "trigraph-blends",
            "trigraphs-review",
            "advanced-preview",
            "tion-ture",
            "sion-ssion",
            "ough",
            "advanced-review",
            "colors",
            "animals",
            "family",
            "feelings",
            "daily-verbs",
            "foods",
            "drinks",
            "numbers",
            "calendar",
            "vocabulary-foundation",
            "level-two-grammar",
            "demonstratives",
            "pronouns",
            "possessive-nouns",
            "vocabulary-quiz",
            "review",
        ]

        for sheet in expected_sheets:
            with self.subTest(sheet=sheet):
                response = self.client.get(f"/sounds/worksheet/?sheet={sheet}")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'data-sheet="{sheet}"')

    def test_animals_worksheet_contains_enhanced_sections(self):
        response = self.client.get("/sounds/worksheet/?sheet=animals")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-sheet="animals"')
        self.assertContains(response, "Pets")
        self.assertContains(response, "Farm Animals")
        self.assertContains(response, "Wild Animals")
        self.assertContains(response, "Sea Animals")
        self.assertContains(response, "Small Creatures")
        self.assertContains(response, "shark lives in")
        self.assertContains(response, "Animal Mini Story")
        self.assertContains(response, "What animal can run?")

    def test_foods_worksheet_contains_enhanced_sections(self):
        response = self.client.get("/sounds/worksheet/?sheet=foods")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-sheet="foods"')
        self.assertContains(response, "Fruits")
        self.assertContains(response, "Vegetables")
        self.assertContains(response, "Daily Meals")
        self.assertContains(response, "Snacks")
        self.assertContains(response, "Sweets")
        self.assertContains(response, "Healthy Food")
        self.assertContains(response, "apple is")
        self.assertContains(response, "carrot is")
        self.assertContains(response, "Food Mini Story")
        self.assertContains(response, "What fruit do I eat?")
        self.assertContains(response, "What do I drink?")

    def test_calendar_worksheet_contains_enhanced_sections(self):
        response = self.client.get("/sounds/worksheet/?sheet=calendar")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-sheet="calendar"')
        self.assertContains(response, "Days")
        self.assertContains(response, "Months")
        self.assertContains(response, "Monday is")
        self.assertContains(response, "March is")
        self.assertContains(response, "Calendar Mini Story")
        self.assertContains(response, "What day is today?")
        self.assertContains(response, "What month is my birthday?")

    def test_level_two_grammar_worksheets_contain_required_lessons(self):
        expected = {
            "level-two-grammar": ["Level 2 Grammar", "Demonstratives", "Pronouns", "Possessive Nouns"],
            "demonstratives": ["This is my pen.", "These are my books.", "This / These / Those"],
            "pronouns": ["I am a student.", "She reads books.", "Subject Pronouns", "Object Pronouns"],
            "possessive-nouns": ["Ali's bag is blue.", "the students' books", "plural owner"],
        }

        for sheet, texts in expected.items():
            with self.subTest(sheet=sheet):
                response = self.client.get(f"/sounds/worksheet/?sheet={sheet}")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'data-sheet="{sheet}"')
                for text in texts:
                    self.assertContains(response, text)
