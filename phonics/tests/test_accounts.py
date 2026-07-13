import json

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings

from phonics.models import StudentProfile


@override_settings(DISABLE_AUTO_SEED=True)
class AccountsFoundationTests(TestCase):
    def test_register_page_returns_success(self):
        response = self.client.get("/accounts/register/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phonics Game Lab")
        self.assertContains(response, "/privacy/")
        self.assertContains(response, "/terms/")

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
                "school": "Test School",
                "parent_phone": "0500000000",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="student1")
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.student_name, "Test Student")
        self.assertEqual(profile.school, "Test School")
        self.assertEqual(profile.parent_phone, "0500000000")

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
                "school": "New School",
                "parent_phone": "0511111111",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.student_name, "New Name")
        self.assertEqual(profile.school, "New School")
        self.assertEqual(profile.parent_phone, "0511111111")

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
        vip_group, _ = Group.objects.get_or_create(name="VIP")
        user.groups.add(vip_group)
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
