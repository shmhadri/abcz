import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import StudentProfile
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class AccountsFoundationTests(TestCase):
    def test_register_page_returns_success(self):
        response = self.client.get("/accounts/register/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phonics Game Lab")
        self.assertContains(response, "/privacy/")
        self.assertContains(response, "/terms/")
        self.assertContains(response, "المدينة")
        self.assertNotContains(response, "المدرسة")
        self.assertNotContains(response, "الصف")
        self.assertNotContains(response, "جوال ولي الأمر")

    def test_profile_interfaces_and_privacy_describe_the_same_fields(self):
        letters = self.client.get("/").content.decode("utf-8")
        privacy = self.client.get("/privacy/").content.decode("utf-8")

        self.assertIn('id="profileName"', letters)
        self.assertIn('id="profileCity"', letters)
        self.assertIn('id="profileParentPhone"', letters)
        self.assertNotIn('id="profileSchool"', letters)
        self.assertNotIn('id="profilePhone"', letters)
        for label in ("الاسم", "البريد الإلكتروني", "رقم الجوال", "المدينة", "مدة الاحتفاظ"):
            self.assertIn(label, privacy)

    def test_login_page_returns_success(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phonics Game Lab")
        self.assertContains(response, "/guide/")

    def test_register_creates_student_profile(self):
        response = self.client.post(
            "/accounts/register/",
            data={
                "username": "student1",
                "email": "student@example.com",
                "student_name": "Test Student",
                "parent_phone": "0500000000",
                "city": "Riyadh",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="student1")
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.student_name, "Test Student")
        self.assertEqual(profile.city, "Riyadh")
        self.assertEqual(profile.school, "")
        self.assertEqual(profile.parent_phone, "0500000000")

    def test_register_rejects_phone_with_letters(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "invalid-phone",
                "email": "invalid-phone@example.com",
                "student_name": "طالب تجريبي",
                "grade": "3",
                "school": "Test School",
                "parent_phone": "05AB123456",
                "city": "Riyadh",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أدخل رقم جوال سعودي صحيحًا")
        self.assertFalse(User.objects.filter(username="invalid-phone").exists())

    def test_register_normalizes_saudi_international_phone(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "normalized-phone",
                "email": "normalized-phone@example.com",
                "student_name": "طالب تجريبي",
                "grade": "3",
                "school": "Test School",
                "parent_phone": "+966501234567",
                "city": "Jeddah",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        profile = StudentProfile.objects.get(user__username="normalized-phone")
        self.assertEqual(profile.parent_phone, "0501234567")

    def test_register_normalizes_arabic_phone_digits(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "arabic-phone",
                "email": "arabic-phone@example.com",
                "student_name": "طالب تجريبي",
                "grade": "3",
                "school": "Test School",
                "parent_phone": "٠٥٠١٢٣٤٥٦٧",
                "city": "الرياض",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        profile = StudentProfile.objects.get(user__username="arabic-phone")
        self.assertEqual(profile.parent_phone, "0501234567")

    def test_register_rejects_case_insensitive_duplicate_email(self):
        User.objects.create_user(
            username="existing-email",
            email="parent@example.com",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "new-email-user",
                "email": "PARENT@example.com",
                "student_name": "طالب تجريبي",
                "grade": "3",
                "school": "Test School",
                "parent_phone": "0501234567",
                "city": "Dammam",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "البريد الإلكتروني مرتبط بحساب موجود")
        self.assertFalse(User.objects.filter(username="new-email-user").exists())

    def test_logout_clears_session(self):
        user = User.objects.create_user(username="student2", password="StrongPass123!")
        self.client.login(username="student2", password="StrongPass123!")

        response = self.client.post("/accounts/logout/")

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(User.objects.filter(id=user.id).exists())

    def test_logout_get_is_not_allowed(self):
        user = User.objects.create_user(username="logout-get", password="StrongPass123!")
        self.client.force_login(user)
        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_rejects_external_next_redirect(self):
        User.objects.create_user(username="redirect-user", password="StrongPass123!")
        response = self.client.post(
            "/accounts/login/?next=https://evil.example/phish",
            {"username": "redirect-user", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

    def test_login_accepts_internal_next_redirect(self):
        User.objects.create_user(username="redirect-local", password="StrongPass123!")
        response = self.client.post(
            "/accounts/login/?next=/profile/",
            {"username": "redirect-local", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/profile/")

    def test_profile_api_updates_authenticated_profile(self):
        user = User.objects.create_user(username="student3", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name="Old Name")
        self.client.login(username="student3", password="StrongPass123!")

        response = self.client.post(
            "/accounts/profile/",
            data=json.dumps({
                "student_name": "New Name",
                "city": "Makkah",
                "parent_phone": "0511111111",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.student_name, "New Name")
        self.assertEqual(profile.city, "Makkah")
        self.assertEqual(profile.school, "")
        self.assertEqual(profile.parent_phone, "0511111111")

    def test_profile_api_rejects_phone_with_letters(self):
        user = User.objects.create_user(username="profile-phone", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name="Old Name")
        self.client.force_login(user)

        response = self.client.post(
            "/accounts/profile/",
            data=json.dumps({
                "display_name": "Learner",
                "student_name": "New Name",
                "city": "Madinah",
                "parent_phone": "0500ABC000",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_phone", response.json()["errors"])

    def test_login_and_register_responses_are_not_cacheable(self):
        for url in ("/accounts/login/", "/accounts/register/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("no-cache", response.headers["Cache-Control"])

    def test_letters_menu_has_one_guest_login_link_and_no_profile_trigger(self):
        response = self.client.get("/")
        menu_html = response.content.decode().split('id="userDropdown"', 1)[1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(menu_html.count('href="/accounts/login/"'), 1)
        self.assertNotIn('id="profileBtn"', menu_html)
        self.assertNotIn("لوحة المتصدرين", menu_html)

    def test_letters_page_loads_account_context(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const IS_AUTHENTICATED = false;")
        self.assertContains(response, "const IS_PREMIUM_USER = false;")
        self.assertContains(response, "const IS_VIP_USER = false;")
        self.assertContains(response, 'window.LEVEL_ONE_PLAN = "free";')
        self.assertNotContains(response, 'id="birdTutorLocked"')
        self.assertNotContains(response, 'id="birdTutor" aria-label="Phonics Bird Tutor"')

    def test_vip_user_sees_bird_tutor_in_level_one_policy(self):
        user = User.objects.create_user(username="vipstudent", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name="VIP Student", is_vip=True)
        grant_active_subscription(user, "vip")
        self.client.login(username="vipstudent", password="StrongPass123!")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const IS_VIP_USER = true;")
        self.assertContains(response, 'id="birdTutor"')
        self.assertContains(response, 'id="birdAskBtn"')
        self.assertNotContains(response, 'id="birdTutorLocked"')

    @override_settings(DEBUG=True, DEV_UNLOCK_VIP_BIRD=True)
    def test_developer_preview_does_not_unlock_bird_in_level_one_policy(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const IS_VIP_USER = false;")
        self.assertNotContains(response, 'id="birdTutor"')
        self.assertNotContains(response, 'id="birdAskBtn"')
        self.assertNotContains(response, 'id="birdRepeatBtn"')
        self.assertNotContains(response, "Developer VIP Preview")
        self.assertNotContains(response, 'id="birdTutorLocked"')

    @override_settings(DEBUG=True, DEV_UNLOCK_VIP_BIRD=False)
    def test_developer_preview_can_be_disabled(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const IS_VIP_USER = false;")
        self.assertNotContains(response, 'id="birdTutorLocked"')
        self.assertNotContains(response, 'id="birdAskBtn"')
        self.assertNotContains(response, "Developer VIP Preview")
