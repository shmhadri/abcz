"""Tests for the Level 2 printable vocabulary worksheet builders.

The old worksheet printed exercises that gave the answer away:

* "match the word to the picture" printed `red -> (red icon)` already paired,
* "circle the correct translation" printed the correct translation first,
  followed by the literal words "review" and "other",
* "sort the words" offered a single category, so there was nothing to sort.

These tests pin the properties that make the replacements real exercises, and
pin determinism so a re-printed worksheet is identical to the first print.
"""
from django.test import SimpleTestCase

from phonics.views import (
    FOUNDATION_VOCABULARY_CATEGORIES,
    WORKSHEET_CHOICE_OPTIONS,
    WORKSHEET_TABLE_CHUNK,
    build_vocabulary_choice_exercise,
    build_vocabulary_match_exercise,
    build_vocabulary_sort_exercise,
    build_vocabulary_spelling_exercise,
    build_vocabulary_worksheets,
)


def find_category(worksheet_key):
    return next(
        category
        for category in FOUNDATION_VOCABULARY_CATEGORIES
        if category["worksheet"] == worksheet_key
    )


class MatchExerciseTests(SimpleTestCase):
    def setUp(self):
        self.words = find_category("colors")["words"]
        self.exercise = build_vocabulary_match_exercise(self.words)

    def test_words_and_pictures_are_separate_columns(self):
        self.assertTrue(self.exercise["words"])
        self.assertEqual(len(self.exercise["words"]), len(self.exercise["pictures"]))

    def test_columns_are_not_pre_matched(self):
        # If row i held the picture for word i the drill would be pointless.
        words = [row["word"] for row in self.exercise["words"]]
        icons = [row["icon"] for row in self.exercise["pictures"]]
        source_icon_by_word = {item["word"]: item["icon"] for item in self.words}
        aligned = sum(
            1 for word, icon in zip(words, icons) if source_icon_by_word[word] == icon
        )
        self.assertEqual(aligned, 0, "the picture column is still aligned with the words")

    def test_every_word_still_has_its_picture_somewhere(self):
        # Scrambled, but solvable: no pair may be dropped.
        words = {row["word"] for row in self.exercise["words"]}
        icons = {row["icon"] for row in self.exercise["pictures"]}
        expected_icons = {
            item["icon"] for item in self.words if item["word"] in words
        }
        self.assertEqual(icons, expected_icons)

    def test_columns_are_labelled_for_drawing_lines(self):
        self.assertEqual([row["number"] for row in self.exercise["words"]][:3], [1, 2, 3])
        self.assertEqual([row["letter"] for row in self.exercise["pictures"]][:3], ["A", "B", "C"])

    def test_handles_tiny_input_without_crashing(self):
        self.assertEqual(build_vocabulary_match_exercise([]), {"words": [], "pictures": []})
        single = [{"word": "red", "icon": "R", "arabic": "أحمر"}]
        self.assertEqual(build_vocabulary_match_exercise(single), {"words": [], "pictures": []})


class ChoiceExerciseTests(SimpleTestCase):
    def setUp(self):
        self.words = find_category("colors")["words"]
        self.questions = build_vocabulary_choice_exercise(self.words)

    def test_questions_are_produced(self):
        self.assertTrue(self.questions)

    def test_every_question_offers_the_configured_number_of_options(self):
        for question in self.questions:
            with self.subTest(word=question["word"]):
                self.assertEqual(len(question["options"]), WORKSHEET_CHOICE_OPTIONS)

    def test_the_correct_answer_is_among_the_options(self):
        for question in self.questions:
            with self.subTest(word=question["word"]):
                self.assertIn(question["answer"], question["options"])

    def test_options_are_distinct(self):
        for question in self.questions:
            with self.subTest(word=question["word"]):
                self.assertEqual(len(set(question["options"])), len(question["options"]))

    def test_distractors_are_real_translations_not_filler(self):
        # The old sheet used the literal strings "مراجعة" and "غير ذلك".
        valid = {item["arabic"] for item in self.words}
        for question in self.questions:
            for option in question["options"]:
                with self.subTest(word=question["word"], option=option):
                    self.assertIn(option, valid)

    def test_the_answer_is_not_always_in_the_same_position(self):
        positions = {
            question["options"].index(question["answer"]) for question in self.questions
        }
        self.assertGreater(
            len(positions), 1, "the correct answer sits in a fixed slot every time"
        )

    def test_answer_letter_points_at_the_answer(self):
        for question in self.questions:
            index = ord(question["answer_letter"]) - ord("A")
            with self.subTest(word=question["word"]):
                self.assertEqual(question["options"][index], question["answer"])

    def test_handles_tiny_input_without_crashing(self):
        self.assertEqual(build_vocabulary_choice_exercise([]), [])
        self.assertEqual(
            build_vocabulary_choice_exercise([{"word": "red", "arabic": "أحمر"}]), []
        )


class SpellingExerciseTests(SimpleTestCase):
    def setUp(self):
        self.words = find_category("colors")["words"]
        self.drills = build_vocabulary_spelling_exercise(self.words)

    def test_drills_are_produced(self):
        self.assertTrue(self.drills)

    def test_each_drill_hides_at_least_one_letter(self):
        for drill in self.drills:
            with self.subTest(answer=drill["answer"]):
                self.assertIn("_", drill["masked"])

    def test_masked_word_keeps_the_original_length(self):
        for drill in self.drills:
            with self.subTest(answer=drill["answer"]):
                self.assertEqual(len(drill["masked"]), len(drill["answer"]))

    def test_first_and_last_letters_stay_visible(self):
        # A child needs an anchor at both ends to read the word.
        for drill in self.drills:
            with self.subTest(answer=drill["answer"]):
                self.assertNotEqual(drill["masked"][0], "_")
                self.assertNotEqual(drill["masked"][-1], "_")

    def test_two_letter_words_are_skipped(self):
        drills = build_vocabulary_spelling_exercise(
            [{"word": "an", "arabic": "x", "icon": ""}]
        )
        self.assertEqual(drills, [])

    def test_short_words_across_all_categories_stay_readable(self):
        for category in FOUNDATION_VOCABULARY_CATEGORIES:
            for drill in build_vocabulary_spelling_exercise(category["words"]):
                visible = sum(1 for ch in drill["masked"] if ch != "_")
                with self.subTest(category=category["worksheet"], answer=drill["answer"]):
                    self.assertGreaterEqual(
                        visible, 2, "too much of the word is hidden to be solvable"
                    )


class SortExerciseTests(SimpleTestCase):
    def setUp(self):
        self.category = find_category("colors")
        self.exercise = build_vocabulary_sort_exercise(
            self.category, FOUNDATION_VOCABULARY_CATEGORIES
        )

    def test_more_than_one_column_is_offered(self):
        # Sorting into a single bucket is not a task.
        self.assertIsNotNone(self.exercise)
        self.assertGreaterEqual(len(self.exercise["columns"]), 2)

    def test_bank_contains_words_from_every_column(self):
        labels = {column["title_ar"] for column in self.exercise["columns"]}
        used = {entry["category"] for entry in self.exercise["bank"]}
        self.assertEqual(used, labels)

    def test_no_two_neighbouring_words_share_a_category(self):
        # Otherwise the layout itself leaks the answer.
        categories = [entry["category"] for entry in self.exercise["bank"]]
        adjacent = [
            (first, second)
            for first, second in zip(categories, categories[1:])
            if first == second
        ]
        self.assertEqual(adjacent, [], "the bank is printed grouped by category")

    def test_every_category_contributes_the_same_number_of_words(self):
        counts = {}
        for entry in self.exercise["bank"]:
            counts[entry["category"]] = counts.get(entry["category"], 0) + 1
        self.assertEqual(len(set(counts.values())), 1, "the bank is unbalanced")

    def test_returns_none_when_there_is_nothing_to_sort_against(self):
        self.assertIsNone(build_vocabulary_sort_exercise(self.category, [self.category]))


class WorksheetAssemblyTests(SimpleTestCase):
    def setUp(self):
        self.worksheets = build_vocabulary_worksheets()

    def test_one_worksheet_per_category(self):
        self.assertEqual(len(self.worksheets), len(FOUNDATION_VOCABULARY_CATEGORIES))
        self.assertEqual(
            [sheet["worksheet"] for sheet in self.worksheets],
            [category["worksheet"] for category in FOUNDATION_VOCABULARY_CATEGORIES],
        )

    def test_every_worksheet_has_every_exercise(self):
        for sheet in self.worksheets:
            with self.subTest(worksheet=sheet["worksheet"]):
                self.assertTrue(sheet["match"]["words"])
                self.assertTrue(sheet["choices"])
                self.assertTrue(sheet["spelling"])
                self.assertTrue(sheet["sentences"])
                self.assertIsNotNone(sheet["sort"])

    def test_long_word_lists_are_split_for_printing(self):
        # foods has 40 words and animals 31; one 40-row table does not print well.
        for sheet in self.worksheets:
            with self.subTest(worksheet=sheet["worksheet"]):
                for chunk in sheet["table_chunks"]:
                    self.assertLessEqual(len(chunk), WORKSHEET_TABLE_CHUNK)

    def test_chunking_preserves_every_word(self):
        for sheet, category in zip(self.worksheets, FOUNDATION_VOCABULARY_CATEGORIES):
            flattened = [item for chunk in sheet["table_chunks"] for item in chunk]
            with self.subTest(worksheet=sheet["worksheet"]):
                self.assertEqual(
                    [item["word"] for item in flattened],
                    [item["word"] for item in category["words"]],
                )

    def test_output_is_deterministic(self):
        # A re-printed worksheet must be identical, otherwise an answer key
        # produced from the first print stops matching.
        again = build_vocabulary_worksheets()
        self.assertEqual(self.worksheets, again)

    def test_builder_does_not_mutate_the_source_data(self):
        before = [len(category["words"]) for category in FOUNDATION_VOCABULARY_CATEGORIES]
        build_vocabulary_worksheets()
        after = [len(category["words"]) for category in FOUNDATION_VOCABULARY_CATEGORIES]
        self.assertEqual(before, after)
