from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .security import rate_limit


password_reset = rate_limit(
    "password-reset",
    limit_setting="RATE_LIMIT_PASSWORD_RESET",
    default=5,
    window=3600,
)(auth_views.PasswordResetView.as_view(
    template_name="accounts/password_reset_form.html",
    email_template_name="accounts/password_reset_email.txt",
    subject_template_name="accounts/password_reset_subject.txt",
    success_url=reverse_lazy("password_reset_done"),
))

password_reset_done = auth_views.PasswordResetDoneView.as_view(
    template_name="accounts/password_reset_done.html",
)

password_reset_confirm = auth_views.PasswordResetConfirmView.as_view(
    template_name="accounts/password_reset_confirm.html",
    success_url=reverse_lazy("password_reset_complete"),
)

password_reset_complete = auth_views.PasswordResetCompleteView.as_view(
    template_name="accounts/password_reset_complete.html",
)
