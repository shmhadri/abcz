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
