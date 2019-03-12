from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client

from rest_framework import status
from rest_framework.test import APITestCase

from utils.random_support import RandomSupport

from duty_api.serializers import DutySerializer
from duty_api.models import Duty, DutyManager

User = get_user_model()

class DutyAPITests(APITestCase, RandomSupport):
    """Test endpoints in `duties/api/` API.
    """
    client = Client()

    def create_user(self, name=None, email=None, password=None):
        """Helper that create mock user that is:
            - is_active (bool) True
            - is_staff (bool) & is_superuser (bool) are False
            - credential using email & password field

            Args:
                name (str): name for user, generate random name if None
                email (str): email for credential, generate random .@example.com email if None
                password (str): password for credential, generate random password if None
            
            Returns:
                user (User)
        """
        # random generate value if not specified
        name = name if name else self.generate_name()
        email = email if email else self.generate_email()
        password = password if password else self.generate_alphanumeric()

        # create user with specified model fields
        user = User.objects.create_user(
            name=name, email=email, password=password
        )
        user.save()

        return user

    def setUp(self):
        # setup duty manager
        self.duty_manager = DutyManager()

        # setup mock user
        self.email = self.generate_email()
        self.password = self.generate_alphanumeric(10)
        self.user = self.create_user(email=self.email, password=self.password)

    def test_request_get_started_duty(self):
        """Test GET duty is valid only if active duty is associated with 
            the authenticated user.
        """
        # initially no duty associated, hence DoesNotExist is raised
        with self.assertRaises(Duty.DoesNotExist):
            duty = self.user.duty

        # authenticate & login user 
        is_logged_in = self.client.login(email=self.email, password=self.password)
        self.assertTrue(is_logged_in)

        # GET expect Http400 or 404 since no duty ever associated with user before.
        response = self.client.get(reverse('duty'))
        self.assertIn(response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
        )

        # start/create duty associated with user internally
        self.duty_manager.start_duty(self.user)

        # verify duty is created in duty manager and associated to user
        self.assertIsNotNone(self.duty_manager.duty)
        self.assertIs(self.duty_manager.duty, self.user.duty)

        # GET expect Http200 success since duty is associated with authenticated user
        serialized = DutySerializer(self.user.duty)
        response = self.client.get(reverse('duty'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('payload'), serialized.data)

    def test_request_post_create_duty(self):
        """Test POST duty is valid if user has not associated with any duty and
            no duty is active in duty manager.
        """
        # initially no duty associated, hence DoesNotExist is raised
        with self.assertRaises(Duty.DoesNotExist):
            duty = self.user.duty
        
        # initially no duty is active in duty manager
        self.assertIsNone(self.duty_manager.duty)

        # authenticate & login user
        is_logged_in = self.client.login(email=self.email, password=self.password)
        self.assertTrue(is_logged_in)

        # POST expect Http200 success since creation is valid
        response = self.client.post(reverse('duty'))
        self.user.refresh_from_db() # refresh to get one-one duty
        serialized = DutySerializer(self.user.duty)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data.get('payload'), serialized.data)

    def test_request_delete_duty(self):
        """Test DELETE duty is valid only if duty has been finished.
        """
        pass

    def tearDown(self):
        # reset duty manager from any duty associated
        duty_manager = DutyManager()
        duty_manager.reset()
