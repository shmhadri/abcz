from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# قائمة الحروف من A إلى Z لاستخدامها كـ choices
LETTERS = [
    (chr(i), chr(i))
    for i in range(ord("A"), ord("Z") + 1)
]


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


class LetterProgress(models.Model):
    """
    تقدم الطالب في حرف واحد (A أو B أو ...).
    كل طالب يجب أن يكون له سجل واحد فقط لكل حرف.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="progress_entries",  # للوصول: student.progress_entries.all()
        verbose_name="الطالب",
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

    class Meta:
        verbose_name = "تقدم حرف"
        verbose_name_plural = "تقدم الحروف"
        unique_together = ("student", "letter")  # طالب واحد لا يملك سجلين لنفس الحرف
        indexes = [
            models.Index(fields=["student", "letter"]),
            models.Index(fields=["letter"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.name} - {self.letter} ({self.score}%)"

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
        self.student.recalculate_progress()


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
