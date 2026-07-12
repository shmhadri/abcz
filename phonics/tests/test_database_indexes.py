from django.test import SimpleTestCase

from phonics import models


class DatabaseIndexDefinitionTests(SimpleTestCase):
    def assert_model_has_indexes(self, model, expected_names):
        actual_names = {index.name for index in model._meta.indexes}
        missing = set(expected_names) - actual_names
        self.assertFalse(
            missing,
            f"{model.__name__} is missing database indexes: {sorted(missing)}",
        )

    def test_cvc_content_indexes_match_paginated_read_paths(self):
        self.assert_model_has_indexes(
            models.CVCWord,
            {"cvc_word_order_id_idx", "cvc_word_sheet_idx"},
        )
        self.assert_model_has_indexes(
            models.CVCSentence,
            {"cvc_sentence_order_id_idx", "cvc_sentence_sheet_idx"},
        )
        self.assert_model_has_indexes(
            models.CVCStory,
            {"cvc_story_order_id_idx", "cvc_story_sheet_idx"},
        )

    def test_leaderboard_indexes_cover_common_filters(self):
        self.assert_model_has_indexes(
            models.Student,
            {"student_score_name_idx", "student_grade_name_idx"},
        )
        self.assert_model_has_indexes(
            models.StudentProfile,
            {"student_profile_grade_idx"},
        )
        self.assert_model_has_indexes(
            models.LetterProgress,
            {"letter_student_time_idx", "letter_user_updated_idx"},
        )
        self.assert_model_has_indexes(
            models.EnglishFoundationProgress,
            {"english_progress_last_idx", "english_progress_user_last_idx"},
        )

    def test_admin_and_review_queue_indexes_cover_common_filters(self):
        self.assert_model_has_indexes(
            models.BirdReviewItem,
            {"bird_review_user_queue_idx"},
        )
        self.assert_model_has_indexes(
            models.PaymentOrder,
            {"payment_status_created_idx", "payment_method_status_idx"},
        )
        self.assert_model_has_indexes(
            models.BankTransferProof,
            {"bank_proof_status_created_idx"},
        )

    def test_topgoal_indexes_cover_unit_ordering(self):
        self.assert_model_has_indexes(
            models.TopGoalUnit,
            {"topgoal_unit_grade_num_idx"},
        )
        self.assert_model_has_indexes(
            models.TopGoalVocabulary,
            {"topgoal_vocab_unit_order_idx"},
        )
        self.assert_model_has_indexes(
            models.TopGoalSentence,
            {"topgoal_sent_unit_order_idx"},
        )
        self.assert_model_has_indexes(
            models.TopGoalQuiz,
            {"topgoal_quiz_unit_order_idx"},
        )
