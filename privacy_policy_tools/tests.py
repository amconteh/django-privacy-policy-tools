from django.test import TestCase
from django.contrib.auth.models import User
from .models import PrivacyPolicy, PrivacyPolicyConfirmation
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import PrivacyPolicy, PrivacyPolicyConfirmation, OneTimeToken
from .middleware import PrivacyPolicyMiddleware
from . import utils

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

class PrivacyPolicyVersioningTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        # Create an initial policy
        self.policy_v1 = PrivacyPolicy.objects.create(
            title="Test Policy",
            text="Initial content",
            confirm_checkbox=True,
            confirm_checkbox_text="I agree",
            confirm_button_text="Submit",
            active=True,
            version=1
        )
        
    def test_version_confirmation(self):
        # Confirm first version of policy
        confirmation = PrivacyPolicyConfirmation.objects.create(
            privacy_policy=self.policy_v1,
            user=self.user,
            confirmed_at=timezone.now()
        )
        
        # Create a new version of the policy
        self.policy_v1.active = False
        self.policy_v1.save()
        
        policy_v2 = PrivacyPolicy.objects.create(
            title="Test Policy",
            text="Updated content",
            confirm_checkbox=True,
            confirm_checkbox_text="I agree",
            confirm_button_text="Submit",
            active=True,
            version=2
        )
        
        # Setup the client and log in
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        with self.settings(PRIVACY_POLICY_TOOLS={'ENABLED': True}):
            # Access a protected page
            response = self.client.get('/dashboard/')  # Adjust to a valid URL in your app
            
            # Check if we're redirected to the confirmation page for v2
            confirm_url = reverse('privacy_policy_tools.views.confirm', args=[policy_v2.id])
            self.assertRedirects(response, confirm_url)

class TokenSecurityTest(TestCase):
    def test_token_generation_security(self):
        # Create required objects for token generation
        user = User.objects.create_user('tokenuser', 'token@example.com', 'password')
        policy = PrivacyPolicy.objects.create(
            title="Token Policy",
            text="Token test content",
            active=True
        )
        confirmation = PrivacyPolicyConfirmation.objects.create(
            privacy_policy=policy,
            user=user
        )
        
        # Generate multiple tokens and ensure uniqueness
        tokens = set()
        for _ in range(100):
            token = OneTimeToken.create_token(confirmation)
            tokens.add(token.token)
            # Clean up for next iteration
            token.delete()
        
        # If tokens are truly random and secure, we should have 100 unique tokens
        self.assertEqual(len(tokens), 100, "Generated tokens should be unique")
        
        # Check token length
        for token_str in tokens:
            self.assertEqual(len(token_str), OneTimeToken.LENGTH)

class MiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = PrivacyPolicyMiddleware(lambda r: r)
        
        # Create test user and group
        self.user = User.objects.create_user('middleware_user', 'middleware@example.com', 'password')
        self.group = Group.objects.create(name='TestGroup')
        
        # Create policies
        self.general_policy = PrivacyPolicy.objects.create(
            title="General Policy",
            text="General policy content",
            active=True,
            version=1
        )
        
        self.group_policy = PrivacyPolicy.objects.create(
            title="Group Policy",
            text="Group policy content",
            active=True,
            version=1,
            for_group=self.group
        )
    
    def test_policy_applies_to_user(self):
        # General policy should apply to all users
        self.assertTrue(
            self.middleware._policy_applies_to_user(self.user, self.general_policy)
        )
        
        # Group policy should not apply to user not in group
        self.assertFalse(
            self.middleware._policy_applies_to_user(self.user, self.group_policy)
        )
        
        # Add user to group and test again
        self.user.groups.add(self.group)
        self.assertTrue(
            self.middleware._policy_applies_to_user(self.user, self.group_policy)
        )