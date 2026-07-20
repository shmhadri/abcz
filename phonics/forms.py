from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import StudentProfile


def normalize_saudi_mobile(value):
    """Normalize common Saudi mobile formats to 05XXXXXXXX."""
    raw_value = (value or "").strip()
    if not raw_value:
        return ""

    raw_value = raw_value.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    compact = raw_value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if compact.startswith("+966"):
        compact = "0" + compact[4:]
    elif compact.startswith("00966"):
        compact = "0" + compact[5:]
    elif compact.startswith("966"):
        compact = "0" + compact[3:]

    if not compact.isascii() or not compact.isdigit() or len(compact) != 10 or not compact.startswith("05"):
        raise ValidationError("أدخل رقم جوال سعودي صحيحًا مثل 05XXXXXXXX.", code="invalid_mobile")
    return compact


class SecureAuthenticationForm(AuthenticationForm):
    """Authentication form with explicit browser security and autofill hints."""

    error_messages = {
        "invalid_login": "اسم المستخدم أو كلمة المرور غير صحيحة.",
        "inactive": "هذا الحساب غير نشط.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = "اسم المستخدم"
        self.fields["password"].label = "كلمة المرور"
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "autocapitalize": "none",
            "spellcheck": "false",
        })
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"}),
    )
    student_name = forms.CharField(
        max_length=200,
        min_length=2,
        label="الاسم",
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    city = forms.CharField(
        max_length=100,
        label="المدينة",
        widget=forms.TextInput(attrs={"autocomplete": "address-level2", "placeholder": "مثال: الرياض"}),
    )
    parent_phone = forms.CharField(
        max_length=20,
        required=True,
        label="رقم الجوال",
        help_text="رقم سعودي يبدأ بـ 05، مثال: 0501234567",
        widget=forms.TextInput(attrs={
            "type": "tel",
            "inputmode": "numeric",
            "autocomplete": "tel",
            "data-saudi-mobile": "",
            "dir": "ltr",
            "maxlength": "14",
            "pattern": r"(?:05\d{8}|(?:\+?966|00966)5\d{8})",
            "placeholder": "05XXXXXXXX",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "student_name", "email", "parent_phone", "city")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "اسم المستخدم"
        self.fields["username"].help_text = "استخدم حروفًا أو أرقامًا دون مسافات."
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "autocapitalize": "none",
            "spellcheck": "false",
        })
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password1"].label = "كلمة المرور"
        self.fields["password1"].help_text = "ثمانية أحرف على الأقل، ولا تستخدم كلمة مرور شائعة أو أرقامًا فقط."
        self.fields["password2"].label = "تأكيد كلمة المرور"
        self.fields["password2"].help_text = "أدخل كلمة المرور نفسها مرة أخرى."

    def clean_username(self):
        username = self.cleaned_data["username"].strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("اسم المستخدم مستخدم بالفعل.", code="duplicate_username")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("البريد الإلكتروني مرتبط بحساب موجود.", code="duplicate_email")
        return email

    def clean_parent_phone(self):
        return normalize_saudi_mobile(self.cleaned_data.get("parent_phone"))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_name=self.cleaned_data["student_name"],
                city=self.cleaned_data["city"],
                parent_phone=self.cleaned_data.get("parent_phone", ""),
            )

        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("display_name", "student_name", "city", "parent_phone")

    def clean_parent_phone(self):
        return normalize_saudi_mobile(self.cleaned_data.get("parent_phone"))
