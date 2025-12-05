from django.db import models

LETTERS = [ (chr(i), chr(i)) for i in range(ord("A"), ord("Z")+1) ]

class Student(models.Model):
    name = models.CharField(max_length=200)
    school = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class LetterProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    letter = models.CharField(max_length=1, choices=LETTERS)
    score = models.IntegerField(default=0)        # نتيجة الاختبار
    passed = models.BooleanField(default=False)   # هل نجح في الحرف؟
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'letter')

    def __str__(self):
        return f"{self.student.name} - {self.letter}"
