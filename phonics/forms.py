from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import StudentProfile


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False, label="البريد الإلكتروني")
    student_name = forms.CharField(max_length=200, label="اسم الطالب")
    grade = forms.CharField(max_length=80, required=False, label="الصف")
    school = forms.CharField(max_length=200, required=False, label="المدرسة")
    parent_phone = forms.CharField(max_length=30, required=False, label="جوال ولي الأمر")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "student_name", "grade", "school", "parent_phone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_name=self.cleaned_data["student_name"],
                grade=self.cleaned_data.get("grade", ""),
                school=self.cleaned_data.get("school", ""),
                parent_phone=self.cleaned_data.get("parent_phone", ""),
            )

        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("display_name", "student_name", "grade", "school", "parent_phone")
