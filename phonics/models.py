from datetime import timedelta
from pathlib import Path
import secrets

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import get_valid_filename

# قائمة الحروف من A إلى Z لاستخدامها كـ choices
LETTERS = [
    (chr(i), chr(i))
    for i in range(ord("A"), ord("Z") + 1)
]


WORDWALL_ALLOWED_PREFIXES = (
    "https://wordwall.net/resource/",
    "https://wordwall.net/play/",
    "https://wordwall.net/ar/resource/",
    "https://www.wordwall.net/ar/resource/",
)

BANK_RECEIPT_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
BANK_RECEIPT_MAX_SIZE = 5 * 1024 * 1024


def validate_bank_transfer_receipt(value):
    extension = Path(value.name or "").suffix.lower()
    if extension not in BANK_RECEIPT_ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Receipt must be a JPG, PNG, or PDF file.",
            code="invalid_receipt_extension",
        )

    size = getattr(value, "size", 0) or 0
    if size > BANK_RECEIPT_MAX_SIZE:
        raise ValidationError(
            "Receipt file must be 5MB or smaller.",
            code="receipt_too_large",
        )

    position = value.tell() if hasattr(value, "tell") else 0
    header = value.read(16)
    if hasattr(value, "seek"):
        value.seek(position)
    signatures = {
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".pdf": (b"%PDF-",),
    }
    if not any(header.startswith(signature) for signature in signatures[extension]):
        raise ValidationError(
            "Receipt content does not match its file extension.",
            code="invalid_receipt_content",
        )


def bank_transfer_receipt_upload_to(instance, filename):
    extension = Path(get_valid_filename(Path(filename or "receipt").name)).suffix.lower()
    random_name = secrets.token_hex(20)
    user_id = instance.user_id or "unknown"
    order_id = instance.payment_order_id or "new"
    return f"bank_transfer_receipts/user_{user_id}/order_{order_id}/{random_name}{extension}"


def validate_wordwall_activity_url(value):
    if not any(str(value).startswith(prefix) for prefix in WORDWALL_ALLOWED_PREFIXES):
        raise ValidationError(
            "Only Wordwall resource and play links are allowed.",
            code="invalid_wordwall_url",
        )


class Student(models.Model):
    """
    يمثل طالب واحد في منصة الحروف/الفونكس.
    يمكن استخدامه لاحقاً مع نظام حسابات (User) إذا حبيت.
    """
    name = models.CharField(
        "اسم الطالب",
        max_length=200
    )
    school = models.CharField(
        "المدرسة",
        max_length=200,
        blank=True
    )
    grade = models.CharField(
        "الصف",
        max_length=80,
        blank=True,
    )
    # مجموع النقاط لجميع الحروف (للاستخدام في الـ Leaderboard)
    total_score = models.PositiveIntegerField(
        "مجموع النقاط",
        default=0,
        help_text="إجمالي النقاط من جميع الحروف، يُحدّث تلقائياً."
    )
    # عدد الحروف التي نجح فيها
    letters_completed = models.PositiveSmallIntegerField(
        "عدد الحروف المكتملة",
        default=0
    )
    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True
    )

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"
        ordering = ["-total_score", "name"]  # يفيد في الـ Leaderboard
        indexes = [
            models.Index(fields=["-total_score", "name"], name="student_score_name_idx"),
            models.Index(fields=["grade", "name"], name="student_grade_name_idx"),
        ]

    def __str__(self) -> str:
        return self.name

    def recalculate_progress(self):
        """
        يعيد حساب:
        - total_score: مجموع درجات جميع الحروف
        - letters_completed: عدد الحروف التي تم اجتيازها بنجاح
        يُنصح باستدعائها بعد تحديث LetterProgress.
        """
        progress_qs = self.progress_entries.all()
        self.total_score = sum(p.score for p in progress_qs)
        self.letters_completed = progress_qs.filter(passed=True).count()
        self.save(update_fields=["total_score", "letters_completed", "updated_at"])


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name="User",
    )
    display_name = models.CharField("Display name", max_length=200, blank=True)
    student_name = models.CharField("اسم الطالب", max_length=200)
    school = models.CharField("المدرسة", max_length=200, blank=True)
    grade = models.CharField("الصف", max_length=80, blank=True)
    parent_phone = models.CharField("جوال ولي الأمر", max_length=30, blank=True)
    is_premium = models.BooleanField("Premium user", default=False)
    is_vip = models.BooleanField("VIP user", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student profile"
        verbose_name_plural = "Student profiles"
        indexes = [
            models.Index(fields=["grade"], name="student_profile_grade_idx"),
        ]

    def __str__(self):
        label = self.display_name or self.student_name or self.user.username
        return f"{label} ({self.user.username})"


class BirdTutorProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bird_tutor_progress",
    )
    xp = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bird tutor progress"
        verbose_name_plural = "Bird tutor progress"

    def __str__(self):
        return f"{self.user.username} - Bird XP {self.xp}"


class BirdReviewItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bird_review_items",
    )
    letter = models.CharField(max_length=1, choices=LETTERS, db_index=True)
    word = models.CharField(max_length=50, db_index=True)
    question_type = models.CharField(max_length=40, blank=True)
    mistakes_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    mastered = models.BooleanField(default=False, db_index=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bird review item"
        verbose_name_plural = "Bird review items"
        unique_together = ("user", "letter", "word")
        ordering = ["mastered", "-updated_at", "letter", "word"]
        indexes = [
            models.Index(fields=["user", "mastered"]),
            models.Index(fields=["user", "letter", "word"]),
            models.Index(fields=["user", "mastered", "-updated_at", "letter", "word"], name="bird_review_user_queue_idx"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.letter}:{self.word}"


class SoundPracticeProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sound_practice_progress",
    )
    completed_items = models.JSONField(default=list, blank=True)
    quiz_attempts = models.PositiveIntegerField(default=0)
    quiz_correct = models.PositiveIntegerField(default=0)
    mic_attempts = models.PositiveIntegerField(default=0)
    mic_success = models.PositiveIntegerField(default=0)
    worksheet_downloads = models.PositiveIntegerField(default=0)
    last_item = models.CharField(max_length=80, blank=True)
    last_payload = models.JSONField(default=dict, blank=True)
    vowel_lessons_completed = models.PositiveIntegerField(default=0)
    practiced_vowels = models.JSONField(default=list, blank=True)
    vowel_quiz_attempts = models.PositiveIntegerField(default=0)
    vowel_quiz_correct = models.PositiveIntegerField(default=0)
    vowel_microphone_attempts = models.PositiveIntegerField(default=0)
    vowel_microphone_success = models.PositiveIntegerField(default=0)
    last_vowel_practiced = models.CharField(max_length=12, blank=True)
    vowel_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sound practice progress"
        verbose_name_plural = "Sound practice progress"

    def __str__(self):
        return f"{self.user.username} - Sounds {len(self.completed_items or [])}"


class LetterProgress(models.Model):
    """
    تقدم الطالب في حرف واحد (A أو B أو ...).
    كل طالب يجب أن يكون له سجل واحد فقط لكل حرف.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="letter_progress_entries",
        null=True,
        blank=True,
        verbose_name="User",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="progress_entries",  # للوصول: student.progress_entries.all()
        verbose_name="الطالب",
        null=True,
        blank=True,
    )
    letter = models.CharField(
        "الحرف",
        max_length=1,
        choices=LETTERS,
        db_index=True  # لتحسين الاستعلامات أثناء عرض التقدم أو التقارير
    )
    score = models.PositiveSmallIntegerField(
        "درجة الحرف",
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="الدرجة من 0 إلى 100."
    )
    passed = models.BooleanField(
        "ناجح في الحرف؟",
        default=False,
        help_text="True إذا تجاوز الحد المطلوب للنجاح في هذا الحرف."
    )
    attempts = models.PositiveIntegerField(
        "عدد المحاولات",
        default=0,
        help_text="كم مرة حاول الطالب اختبار هذا الحرف."
    )
    timestamp = models.DateTimeField(
        "آخر تحديث",
        auto_now=True
    )
    writing_score = models.PositiveSmallIntegerField(default=0)
    words_score = models.PositiveSmallIntegerField(default=0)
    quiz_score = models.PositiveSmallIntegerField(default=0)
    total_score = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    words_practiced_json = models.JSONField(default=list, blank=True)
    mistakes_json = models.JSONField(default=dict, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "تقدم حرف"
        verbose_name_plural = "تقدم الحروف"
        unique_together = ("student", "letter")  # طالب واحد لا يملك سجلين لنفس الحرف
        constraints = [
            models.UniqueConstraint(
                fields=["user", "letter"],
                condition=models.Q(user__isnull=False),
                name="unique_user_letter_progress",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "letter"]),
            models.Index(fields=["user", "letter"]),
            models.Index(fields=["user", "completed"]),
            models.Index(fields=["letter"]),
            models.Index(fields=["student", "timestamp"], name="letter_student_time_idx"),
            models.Index(fields=["user", "last_updated_at"], name="letter_user_updated_idx"),
        ]

    def __str__(self) -> str:
        owner = self.student.name if self.student_id else (self.user.username if self.user_id else "Unknown")
        score = self.total_score if self.user_id else self.score
        return f"{owner} - {self.letter} ({score})"

    def update_from_attempt(self, new_score: int, pass_threshold: int = 70):
        """
        يحدث نتيجة الحرف بناءً على محاولة جديدة:
        - يزيد عدد المحاولات
        - يحفظ أفضل نتيجة
        - يحدد هل الطالب ناجح في الحرف أم لا
        - يحدّث تقدم الطالب الكلي (total_score, letters_completed)
        """
        # زيادة عدد المحاولات
        self.attempts += 1

        # حفظ أفضل نتيجة فقط
        if new_score > self.score:
            self.score = new_score

        # تحديد النجاح بناءً على حد معيّن (مثلاً 70%)
        self.passed = self.score >= pass_threshold
        self.save()

        # تحديث ملخص الطالب
        if self.student_id:
            self.student.recalculate_progress()


class ExternalGame(models.Model):
    REVIEW_PENDING = "pending"
    REVIEW_APPROVED = "approved"
    REVIEW_REJECTED = "rejected"

    REVIEW_STATUS_CHOICES = [
        (REVIEW_PENDING, "Pending"),
        (REVIEW_APPROVED, "Approved"),
        (REVIEW_REJECTED, "Rejected"),
    ]

    letter = models.CharField(
        "Letter",
        max_length=1,
        choices=LETTERS,
        db_index=True,
    )
    title = models.CharField("Title", max_length=200)
    activity_url = models.URLField(
        "Activity URL",
        max_length=500,
        validators=[validate_wordwall_activity_url],
        help_text="Allowed: Wordwall resource and play links.",
    )
    is_premium = models.BooleanField("Premium", default=False)
    is_active = models.BooleanField("Active", default=True)
    review_status = models.CharField(
        "Review status",
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default=REVIEW_PENDING,
        db_index=True,
    )
    notes = models.TextField("Notes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "External game"
        verbose_name_plural = "External games"
        ordering = ["letter", "title"]
        indexes = [
            models.Index(fields=["letter", "is_active", "review_status"]),
        ]

    def clean(self):
        super().clean()
        if self.letter:
            self.letter = self.letter.upper()
        if self.title:
            self.title = self.title.strip()
        if self.activity_url:
            self.activity_url = self.activity_url.strip()
            validate_wordwall_activity_url(self.activity_url)

    def __str__(self):
        return f"{self.letter} - {self.title}"


# ============================================
# نماذج CVC Words Reading System
# ============================================

class CVCWord(models.Model):
    """
    كلمة CVC (Consonant-Vowel-Consonant) مثل CAT, DOG, PEN
    """
    word = models.CharField(
        "الكلمة",
        max_length=10,
        unique=True
    )
    arabic_meaning = models.CharField(
        "المعنى بالعربي",
        max_length=100
    )
    image_url = models.URLField(
        "رابط الصورة",
        max_length=500,
        blank=True,
        help_text="رابط صورة توضيحية للكلمة"
    )
    emoji = models.CharField(
        "الرمز التعبيري",
        max_length=10,
        blank=True,
        default="🎯",
        help_text="رمز تعبيري يمثل الكلمة"
    )
    category = models.CharField(
        "التصنيف",
        max_length=50,
        blank=True,
        help_text="مثل: animals, food, objects"
    )
    
    # ✨ NEW: Word Family and Vowel Sound fields
    word_family = models.CharField(
        "عائلة الكلمة",
        max_length=10,
        blank=True,
        default="",
        db_index=True,
        help_text="مثل: at, an, ig, og - النهاية المشتركة"
    )
    vowel_sound = models.CharField(
        "صوت حرف العلة",
        max_length=5,
        blank=True,
        default="",
        db_index=True,
        help_text="مثل: a, e, i, o, u"
    )
    
    difficulty_level = models.PositiveSmallIntegerField(
        "مستوى الصعوبة",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=سهل جداً، 5=صعب"
    )
    order = models.PositiveIntegerField(
        "الترتيب",
        default=0,
        help_text="ترتيب ظهور الكلمة"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كلمة CVC"
        verbose_name_plural = "كلمات CVC"
        ordering = ["order", "word"]
        indexes = [
            models.Index(fields=['word_family']),
            models.Index(fields=['vowel_sound']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=["order", "id"], name="cvc_word_order_id_idx"),
            models.Index(fields=["vowel_sound", "word_family", "order", "word"], name="cvc_word_sheet_idx"),
        ]

    def __str__(self):
        return f"{self.word} ({self.arabic_meaning})"


class CVCSentence(models.Model):
    """
    جملة مكونة من كلمات CVC وضمائر
    """
    sentence = models.TextField(
        "الجملة الإنجليزية",
        help_text="مثل: The cat sat on the mat."
    )
    arabic_translation = models.TextField(
        "الترجمة العربية"
    )
    difficulty = models.PositiveSmallIntegerField(
        "مستوى الصعوبة",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    time_limit = models.PositiveIntegerField(
        "الحد الزمني بالثواني",
        default=30,
        help_text="الوقت المخصص لقراءة الجملة"
    )
    category = models.CharField(
        "التصنيف",
        max_length=50,
        default='cvc',
        help_text="مثل: cvc, pronouns"
    )
    quiz_data = models.JSONField(
        "بيانات الاختبار",
        blank=True, 
        null=True,
        help_text="سؤال يظهر بعد الجملة"
    )
    emoji = models.CharField(
        "الرمز التعبيري",
        max_length=10,
        blank=True,
        default="📝",
        help_text="رمز تعبيري للجملة"
    )
    order = models.PositiveIntegerField(
        "الترتيب",
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "جملة CVC"
        verbose_name_plural = "جمل CVC"
        ordering = ["order", "difficulty"]
        indexes = [
            models.Index(fields=["order", "id"], name="cvc_sentence_order_id_idx"),
            models.Index(fields=["category", "order", "difficulty"], name="cvc_sentence_sheet_idx"),
        ]

    def __str__(self):
        return self.sentence[:50]


class CVCStory(models.Model):
    """
    قصة قصيرة للأطفال مكونة من كلمات CVC
    """
    title = models.CharField(
        "عنوان القصة",
        max_length=200
    )
    content = models.TextField(
        "محتوى القصة بالإنجليزية",
        help_text="القصة بكلمات CVC بسيطة"
    )
    arabic_explanation = models.TextField(
        "الشرح بالعربي",
        help_text="ترجمة أو شرح القصة للأطفال"
    )
    image_url = models.URLField(
        "رابط صورة القصة",
        max_length=500,
        blank=True
    )
    quiz_data = models.JSONField(
        "بيانات الاختبار",
        blank=True, 
        null=True,
        help_text="JSON structure for questions: [{'question': '...', 'options': ['...'], 'correct': 0, 'feedback_ar': '...'}, ...]"
    )
    difficulty = models.PositiveSmallIntegerField(
        "مستوى الصعوبة",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    order = models.PositiveIntegerField(
        "الترتيب",
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "قصة CVC"
        verbose_name_plural = "قصص CVC"
        ordering = ["order", "difficulty"]
        indexes = [
            models.Index(fields=["order", "id"], name="cvc_story_order_id_idx"),
            models.Index(fields=["order", "difficulty"], name="cvc_story_sheet_idx"),
        ]

    def __str__(self):
        return self.title


class CVCProgress(models.Model):
    """
    تتبع تقدم الطالب في قراءة كلمات وجمل CVC
    """
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="cvc_progress",
        verbose_name="الطالب"
    )
    
    # إحصائيات الكلمات
    words_completed = models.PositiveIntegerField(
        "عدد الكلمات المكتملة",
        default=0
    )
    words_total_score = models.PositiveIntegerField(
        "مجموع نقاط الكلمات",
        default=0
    )
    
    # إحصائيات الجمل
    sentences_completed = models.PositiveIntegerField(
        "عدد الجمل المكتملة",
        default=0
    )
    sentences_total_score = models.PositiveIntegerField(
        "مجموع نقاط الجمل",
        default=0
    )
    best_reading_time = models.FloatField(
        "أفضل وقت قراءة (ثواني)",
        null=True,
        blank=True
    )
    
    # إحصائيات القصص
    stories_completed = models.PositiveIntegerField(
        "عدد القصص المكتملة",
        default=0
    )
    
    # إجمالي
    total_score = models.PositiveIntegerField(
        "المجموع الكلي",
        default=0
    )
    
    last_activity = models.DateTimeField(
        "آخر نشاط",
        auto_now=True
    )
    created_at = models.DateTimeField(
        "تاريخ البدء",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "تقدم CVC"
        verbose_name_plural = "تقدم CVC"

    def __str__(self):
        return f"{self.student.name} - CVC Progress"

    def update_word_score(self, points):
        """تحديث نقاط الكلمات"""
        self.words_completed += 1
        self.words_total_score += points
        self.total_score += points
        self.save()

    def update_sentence_score(self, points, reading_time):
        """تحديث نقاط الجمل"""
        self.sentences_completed += 1
        self.sentences_total_score += points
        self.total_score += points
        
        # تحديث أفضل وقت
        if self.best_reading_time is None or reading_time < self.best_reading_time:
            self.best_reading_time = reading_time
        
        self.save()

    def mark_story_complete(self):
        """تحديد قصة كمكتملة"""
        self.stories_completed += 1
        self.save()


class CVCReadingProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cvc_reading_progress",
    )
    completed_levels = models.JSONField(default=list, blank=True)
    completed_lessons = models.JSONField(default=list, blank=True)
    completed_families = models.JSONField(default=list, blank=True)
    words_practiced = models.JSONField(default=list, blank=True)
    words_mastered = models.JSONField(default=list, blank=True)
    sentences_read = models.PositiveIntegerField(default=0)
    sentences_mastered = models.JSONField(default=list, blank=True)
    sentence_quiz_attempts = models.PositiveIntegerField(default=0)
    sentence_quiz_correct = models.PositiveIntegerField(default=0)
    sentence_microphone_attempts = models.PositiveIntegerField(default=0)
    sentence_microphone_success = models.PositiveIntegerField(default=0)
    last_sentence = models.CharField(max_length=160, blank=True)
    last_sentence_level = models.CharField(max_length=40, blank=True)
    common_sentences_completed = models.PositiveIntegerField(default=0)
    numbers_completed = models.PositiveIntegerField(default=0)
    days_completed = models.PositiveIntegerField(default=0)
    months_completed = models.PositiveIntegerField(default=0)
    sentence_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    sentence_best_time_seconds = models.PositiveIntegerField(default=0)
    sentence_total_time_seconds = models.PositiveIntegerField(default=0)
    stories_completed = models.PositiveIntegerField(default=0)
    stories_started = models.JSONField(default=list, blank=True)
    story_quiz_attempts = models.PositiveIntegerField(default=0)
    story_quiz_correct = models.PositiveIntegerField(default=0)
    story_microphone_attempts = models.PositiveIntegerField(default=0)
    story_microphone_success = models.PositiveIntegerField(default=0)
    last_story = models.CharField(max_length=160, blank=True)
    last_story_level = models.CharField(max_length=60, blank=True)
    story_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    story_best_reading_time = models.PositiveIntegerField(default=0)
    story_needs_review = models.JSONField(default=list, blank=True)
    pronoun_lessons_completed = models.PositiveIntegerField(default=0)
    pronouns_practiced = models.JSONField(default=list, blank=True)
    pronouns_mastered = models.JSONField(default=list, blank=True)
    pronoun_quiz_attempts = models.PositiveIntegerField(default=0)
    pronoun_quiz_correct = models.PositiveIntegerField(default=0)
    pronoun_microphone_attempts = models.PositiveIntegerField(default=0)
    pronoun_microphone_success = models.PositiveIntegerField(default=0)
    last_pronoun = models.CharField(max_length=80, blank=True)
    last_pronoun_level = models.CharField(max_length=80, blank=True)
    pronoun_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    pronouns_needs_review = models.JSONField(default=list, blank=True)
    sight_words_practiced = models.JSONField(default=list, blank=True)
    sight_words_mastered = models.JSONField(default=list, blank=True)
    sight_word_quiz_attempts = models.PositiveIntegerField(default=0)
    sight_word_quiz_correct = models.PositiveIntegerField(default=0)
    fluency_sentences_read = models.PositiveIntegerField(default=0)
    fluency_attempts = models.PositiveIntegerField(default=0)
    best_wpm = models.PositiveIntegerField(default=0)
    best_reading_time = models.PositiveIntegerField(default=0)
    fluency_accuracy = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    fluency_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    question_words_mastered = models.JSONField(default=list, blank=True)
    conversations_completed = models.PositiveIntegerField(default=0)
    action_verbs_mastered = models.JSONField(default=list, blank=True)
    adjectives_mastered = models.JSONField(default=list, blank=True)
    last_fluency_sentence = models.CharField(max_length=180, blank=True)
    last_sight_word = models.CharField(max_length=60, blank=True)
    last_conversation = models.CharField(max_length=120, blank=True)
    fluency_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    quiz_attempts = models.PositiveIntegerField(default=0)
    quiz_correct = models.PositiveIntegerField(default=0)
    mic_attempts = models.PositiveIntegerField(default=0)
    mic_success = models.PositiveIntegerField(default=0)
    last_word = models.CharField(max_length=80, blank=True)
    last_family = models.CharField(max_length=40, blank=True)
    last_level = models.CharField(max_length=40, blank=True)
    cvc_mastery_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    needs_review_words = models.JSONField(default=list, blank=True)
    last_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CVC reading progress"
        verbose_name_plural = "CVC reading progress"
        indexes = [
            models.Index(fields=["updated_at"], name="cvc_reading_updated_idx"),
        ]

    def __str__(self):
        return f"{self.user.username} - CVC Reading {self.cvc_mastery_percentage}%"


class EnglishFoundationProgress(models.Model):
    SECTION_CHOICES = [
        ("vocabulary", "Vocabulary"),
        ("grammar", "Grammar"),
        ("conversations", "Conversations"),
        ("common_sentences", "Common Sentences"),
        ("worksheets", "Worksheets"),
        ("games", "Games"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="english_foundation_progress",
    )
    section = models.CharField(max_length=40, choices=SECTION_CHOICES, db_index=True)
    points = models.PositiveIntegerField(default=0)
    actions_count = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False, db_index=True)
    last_activity_type = models.CharField(max_length=80, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "English foundation progress"
        verbose_name_plural = "English foundation progress"
        unique_together = ("user", "section")
        ordering = ["user", "section"]
        indexes = [
            models.Index(fields=["user", "section"]),
            models.Index(fields=["section", "completed"]),
            models.Index(fields=["last_activity_at"], name="english_progress_last_idx"),
            models.Index(fields=["user", "last_activity_at"], name="english_progress_user_last_idx"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.section} ({self.points})"


class UserSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"
        PENDING_PAYMENT = "pending_payment", "Pending payment"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan_code = models.CharField(max_length=60, db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_PAYMENT, db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    activated_by_payment = models.ForeignKey(
        "PaymentOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activated_subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User subscription"
        verbose_name_plural = "User subscriptions"
        constraints = [
            models.UniqueConstraint(fields=["user", "plan_code"], name="unique_user_subscription_plan"),
        ]
        indexes = [
            models.Index(fields=["user", "status", "expires_at"]),
            models.Index(fields=["plan_code", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan_code} ({self.status})"

    def is_active_now(self):
        now = timezone.now()
        return self.status == self.Status.ACTIVE and self.starts_at <= now and self.expires_at > now


class PaymentOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        INITIATED = "initiated", "Initiated"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"
        AWAITING_BANK_REVIEW = "awaiting_bank_review", "Awaiting bank review"
        BANK_APPROVED = "bank_approved", "Bank approved"
        BANK_REJECTED = "bank_rejected", "Bank rejected"

    class Method(models.TextChoices):
        MOYASAR_CARD = "moyasar_card", "Moyasar card"
        MOYASAR_STCPAY = "moyasar_stcpay", "Moyasar STC Pay"
        BANK_TRANSFER = "bank_transfer", "Bank transfer"

    class Provider(models.TextChoices):
        MOYASAR = "moyasar", "Moyasar"
        MANUAL_BANK = "manual_bank", "Manual bank"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_orders",
    )
    plan_code = models.CharField(max_length=60, db_index=True)
    plan_name = models.CharField(max_length=120)
    duration_days = models.PositiveSmallIntegerField(default=30)
    amount_halalas = models.PositiveIntegerField()
    amount_sar = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default="SAR")
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.PENDING, db_index=True)
    method = models.CharField(max_length=40, choices=Method.choices, db_index=True)
    provider = models.CharField(max_length=40, choices=Provider.choices, db_index=True)
    provider_payment_id = models.CharField(max_length=120, blank=True, db_index=True)
    provider_status = models.CharField(max_length=80, blank=True)
    checkout_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment order"
        verbose_name_plural = "Payment orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["plan_code", "status"]),
            models.Index(fields=["provider", "provider_payment_id"]),
            models.Index(fields=["status", "created_at"], name="payment_status_created_idx"),
            models.Index(fields=["method", "status", "created_at"], name="payment_method_status_idx"),
        ]

    def __str__(self):
        return f"#{self.pk or 'new'} {self.plan_code} {self.amount_sar} {self.currency} ({self.status})"

    @property
    def reference(self):
        return f"ABCZ-{self.pk:06d}" if self.pk else "ABCZ-PENDING"

    def can_activate(self):
        return self.status in {self.Status.PAID, self.Status.BANK_APPROVED}


class BankTransferProof(models.Model):
    class Status(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    payment_order = models.ForeignKey(
        PaymentOrder,
        on_delete=models.CASCADE,
        related_name="bank_proofs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_transfer_proofs",
    )
    bank_name = models.CharField(max_length=120)
    sender_name = models.CharField(max_length=160)
    sender_account_last_digits = models.CharField(max_length=8, blank=True)
    transfer_reference = models.CharField(max_length=120, blank=True)
    transferred_at = models.DateField()
    amount_sar = models.DecimalField(max_digits=8, decimal_places=2)
    receipt_file = models.FileField(
        upload_to=bank_transfer_receipt_upload_to,
        validators=[validate_bank_transfer_receipt],
    )
    note = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_REVIEW, db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_bank_transfer_proofs",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank transfer proof"
        verbose_name_plural = "Bank transfer proofs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["payment_order", "status"]),
            models.Index(fields=["status", "created_at"], name="bank_proof_status_created_idx"),
        ]

    def clean(self):
        super().clean()
        if self.payment_order_id and self.user_id and self.payment_order.user_id != self.user_id:
            raise ValidationError("Bank transfer proof user must match the payment order user.")

    def __str__(self):
        return f"{self.payment_order.reference} - {self.sender_name} ({self.status})"


def activate_subscription_from_payment(payment_order):
    if not payment_order.can_activate():
        raise ValidationError("Payment order is not paid or approved.")

    with transaction.atomic():
        locked_order = PaymentOrder.objects.select_for_update().get(pk=payment_order.pk)
        if locked_order.activated_at:
            return UserSubscription.objects.get(
                user=locked_order.user,
                plan_code=locked_order.plan_code,
            )
        if not locked_order.can_activate():
            raise ValidationError("Payment order is not paid or approved.")

        now = timezone.now()
        current_subscription = UserSubscription.objects.filter(
            user=locked_order.user,
            plan_code=locked_order.plan_code,
        ).first()
        base_start = now
        if (
            current_subscription
            and current_subscription.status == UserSubscription.Status.ACTIVE
            and current_subscription.expires_at
            and current_subscription.expires_at > now
        ):
            base_start = current_subscription.expires_at

        subscription, _ = UserSubscription.objects.update_or_create(
            user=locked_order.user,
            plan_code=locked_order.plan_code,
            defaults={
                "status": UserSubscription.Status.ACTIVE,
                "starts_at": now if base_start == now else current_subscription.starts_at,
                "expires_at": base_start + timedelta(days=locked_order.duration_days),
                "activated_by_payment": locked_order,
            },
        )

        group_names = {
            "basic": "Basic",
            "silver": "Silver",
            "vip": "VIP",
            "diamond": "Diamond",
        }
        group_name = group_names.get(locked_order.plan_code)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            locked_order.user.groups.add(group)

        profile, _ = StudentProfile.objects.get_or_create(
            user=locked_order.user,
            defaults={
                "display_name": locked_order.user.get_full_name() or locked_order.user.username,
                "student_name": locked_order.user.get_full_name() or locked_order.user.username,
                "school": "",
                "parent_phone": "",
            },
        )
        if locked_order.plan_code in {"basic", "silver", "vip", "diamond"}:
            profile.is_premium = True
        if locked_order.plan_code in {"vip", "diamond"}:
            profile.is_vip = True
        profile.save(update_fields=["is_premium", "is_vip", "updated_at"])

        locked_order.activated_at = now
        locked_order.save(update_fields=["activated_at", "updated_at"])
        return subscription


# ============================================
# Top Goal 5 & 6 Models
# ============================================

class TopGoalUnit(models.Model):
    """
    يمثل وحدة دراسية (مثلاً Unit 5: Let's watch a movie!)
    """
    title = models.CharField("عنوان الوحدة", max_length=200)
    subtitle = models.CharField("عنوان فرعي", max_length=200, blank=True)
    description = models.TextField("وصف الوحدة", blank=True)
    grade = models.CharField("الصف", max_length=50, default="Top Goal 6") # user said Top Goal 6
    unit_number = models.IntegerField("رقم الوحدة", default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["grade", "unit_number"], name="topgoal_unit_grade_num_idx"),
        ]

    def __str__(self):
        return f"{self.grade} - {self.title}"

class TopGoalVocabulary(models.Model):
    """
    كلمات ومفردات الوحدة (Movie Genres etc)
    """
    unit = models.ForeignKey(TopGoalUnit, related_name='vocabularies', on_delete=models.CASCADE)
    word = models.CharField("الكلمة/المصطلح", max_length=100)
    arabic_meaning = models.CharField("المعنى بالعربي", max_length=100)
    emoji = models.CharField("الرمز التعبيري", max_length=20, blank=True)
    image_url = models.URLField("رابط الصورة", max_length=500, blank=True)
    audio_file = models.FileField("ملف الصوت", upload_to='topgoal/audio/', blank=True, null=True)
    
    # Example sentence for context
    example_sentence = models.TextField("جملة مثال", blank=True)
    
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "مفردات Top Goal"
        verbose_name_plural = "مفردات Top Goal"
        ordering = ['order']
        indexes = [
            models.Index(fields=["unit", "order"], name="topgoal_vocab_unit_order_idx"),
        ]

    def __str__(self):
        return self.word

class TopGoalSentence(models.Model):
    """
    جمل للقراءة والممارسة
    """
    unit = models.ForeignKey(TopGoalUnit, related_name='sentences', on_delete=models.CASCADE)
    english_text = models.TextField("النص الإنجليزي")
    arabic_translation = models.TextField("الترجمة العربية")
    audio_file = models.FileField("ملف الصوت", upload_to='topgoal/audio/', blank=True, null=True)
    speaker_name = models.CharField("اسم المتحدث", max_length=50, blank=True, help_text="مثلاً: Speaker 1")
    
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "جمل Top Goal"
        verbose_name_plural = "جمل Top Goal"
        ordering = ['order']
        indexes = [
            models.Index(fields=["unit", "order"], name="topgoal_sent_unit_order_idx"),
        ]

    def __str__(self):
        return self.english_text[:50]

class TopGoalQuiz(models.Model):
    """
    أسئلة واختبارات
    """
    unit = models.ForeignKey(TopGoalUnit, related_name='quizzes', on_delete=models.CASCADE)
    question_text = models.TextField("نص السؤال")
    question_type = models.CharField("نوع السؤال", max_length=20, choices=[('mcq', 'اختيار من متعدد'), ('tf', 'صواب/خطأ')], default='mcq')
    
    # Store options as JSON ['option1', 'option2', ...]
    options = models.JSONField("الخيارات", default=list)
    correct_answer = models.CharField("الإجابة الصحيحة", max_length=200)
    
    explanation_ar = models.TextField("شرح الإجابة بالعربي", blank=True)
    
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "اختبار Top Goal"
        verbose_name_plural = "اختبارات Top Goal"
        ordering = ['order']
        indexes = [
            models.Index(fields=["unit", "order"], name="topgoal_quiz_unit_order_idx"),
        ]

    def __str__(self):
        return self.question_text[:50]

