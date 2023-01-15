from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from .models import UserInhaler, AppUser
from django.urls import reverse

# Create your tests here.

class RegistrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup test parameters
        cls.username = 'testuser'
        cls.password = 'xy67@*123abcZ'
        cls.dob = date(2000, 12, 20)
        cls.pollution_limit = 8
        cls.consent = 1

    # Test that we get the registration page and that it uses the correct template
    def test_get_registration_page(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clear/registration/register.html')

    # Test that the registration form
    def test_post_registration_form(self):
        response = self.client.post(
            reverse('register'),
            {
                "username": self.username,
                "password1": self.password,
                "password2": self.password,
                "pollution_limit": self.pollution_limit,
                "dob": self.dob,
                "consent": self.dob
            }
        )

        # Check we get a 302 redirect back after we submit the registration form
        self.assertEqual(response.status_code, 302)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, self.username)
        self.assertEqual(users[0].dob, self.dob)
        self.assertEqual(users[0].pollution_limit, self.pollution_limit)
        self.assertEqual(users[0].consent, self.consent)

class UserInhalerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup test parameters
        cls.username = 'testuser'
        cls.password = 'xy67@*123abcZ'
        cls.dob = date(2000, 12, 20)
        cls.pollution_limit = 8
        cls.consent = 1
        # Setup test parameters
        User = get_user_model()
        cls.user = User.objects.create_user(
            username=cls.username,
            password=cls.password,
            dob=cls.dob,
            pollution_limit=cls.pollution_limit,
            consent=cls.consent
        )


    def test_log_puff(self):

        self.test_user_inhaler = UserInhaler.objects.create(
            user=self.user,
            inhaler_id=1,
            puffs_today=0,
            puffs_remaining=2,
            puffs_per_day=1,
        )
        self.test_user_inhaler.log_puff(self.test_user_inhaler.id)
        updated_user_inhaler = UserInhaler.objects.get(pk=self.test_user_inhaler.id)
        self.assertEqual(updated_user_inhaler.puffs_today, 1)
        self.assertEqual(updated_user_inhaler.puffs_remaining, 1)

        self.test_user_inhaler.log_puff(self.test_user_inhaler.id)
        updated_user_inhaler = UserInhaler.objects.get(pk=self.test_user_inhaler.id)
        self.assertEqual(updated_user_inhaler.puffs_today, 2)
        self.assertEqual(updated_user_inhaler.puffs_remaining, 0)

        self.test_user_inhaler.log_puff(self.test_user_inhaler.id)
        updated_user_inhaler = UserInhaler.objects.get(pk=self.test_user_inhaler.id)
        self.assertEqual(updated_user_inhaler.puffs_today, 2)
        self.assertEqual(updated_user_inhaler.puffs_remaining, 0)
