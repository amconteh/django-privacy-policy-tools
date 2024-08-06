from django.test import TestCase
from django.contrib.auth.models import User
from .models import PrivacyPolicy, PrivacyPolicyConfirmation

class PrivacyPolicyModelTest(TestCase):
    def setUp(self):
        self.policy = PrivacyPolicy.objects.create(
            title="Test Policy",
            text="This is a test policy.",
            active=True
        )

    def test_privacy_policy_creation(self):
        self.assertEqual(self.policy.title, "Test Policy")
        self.assertTrue(self.policy.active)

class PrivacyPolicyConfirmationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.policy = PrivacyPolicy.objects.create(
            title="Test Policy",
            text="This is a test policy.",
            active=True
        )
        self.confirmation = PrivacyPolicyConfirmation.objects.create(
            user=self.user,
            privacy_policy=self.policy
        )

    def test_privacy_policy_confirmation_creation(self):
        self.assertEqual(self.confirmation.user, self.user)
        self.assertEqual(self.confirmation.privacy_policy, self.policy)