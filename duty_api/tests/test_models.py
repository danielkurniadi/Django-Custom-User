from django.test import TestCase
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from utils.random_support import RandomSupport
from duty_api.models import (
    Duty, DutyManager,
    BehalfWithNoUserError,
    CannotStartOverOngoingDuty,
    CannotClearUnfinishedDuty,
)

User = get_user_model()


# import logging
# dblog = logging.getLogger('django.db.backends')
# dblog.setLevel(logging.DEBUG)
# dblog.addHandler(logging.StreamHandler())

class BaseDutyTestCase(TestCase, RandomSupport):
    """Base Class for duty related tests.
    """

    def create_user(self, name=None, email=None, password=None):
        # random generate value if not specified
        name = name if name else self.generate_name()
        email = email if email else self.generate_email()
        password = password if password else self.generate_alphanumeric()

        # create user with specified model fields
        user = User.objects.create(
            name=name, email=email, password=password)

        return user


#############################################################################

class TestDutyModel(BaseDutyTestCase):
    """Test Duty model functionality
    """

    def setUp(self):
        """Setup test data for Test Duty Models.
        """
        # default duty time mark start
        self.delta_task1_start = timedelta(minutes=Duty.TASK1_MARK)
        self.delta_task2_start = timedelta(minutes=Duty.TASK2_MARK)
        self.delta_task3_start = timedelta(minutes=Duty.TASK3_MARK)
        # default duty time mark end
        self.task_window = timedelta(minutes=Duty.TASK_WINDOW)
        self.duty_window = timedelta(minutes=Duty.DUTY_DURATION)

    def test_duty_creation(self):
        """Verify Duty can be created and time marks are correct.
        """
        # initially no duty created
        self.assertEqual(Duty.objects.count(), 0)

        # create user
        name = self.generate_name()
        email = self.generate_email()
        password = self.generate_alphanumeric()
        user = self.create_user(name, email, password)

        # create new Duty with user
        duty = Duty.objects.create(user=user) # auto save

        # verify duty count increases by 1
        self.assertEqual(Duty.objects.count(), 1)
        self.assertIs(duty.user, user)
        self.assertIs(duty, user.duty)

        # verify duty time mark start
        duty_start = duty.duty_start
        self.assertEqual(duty.task1_start, duty_start + self.delta_task1_start)
        self.assertEqual(duty.task2_start, duty_start + self.delta_task2_start)
        self.assertEqual(duty.task3_start, duty_start + self.delta_task3_start)

        # verify duty time mark end
        duty_end = duty.duty_end
        self.assertEqual(duty_end, duty_start + self.duty_window)
        self.assertEqual(duty.task1_end, duty.task1_start + self.task_window)
        self.assertEqual(duty.task2_end, duty.task2_start + self.task_window)
        self.assertEqual(duty.task3_end, duty.task3_start + self.task_window)

        # verify duty's user information
        self.assertEqual(duty.user.name, name)
        self.assertEqual(duty.user.email, email)


    def test_duty_deletion(self):
        """Deleting duty works and will not remove related user.
        """
        # initially no duty created
        self.assertEqual(Duty.objects.count(), 0)

        # create user
        name = "User_one"
        email = "user_one@email.com"
        password = "userpass796"
        user = self.create_user(name, email, password)
        user_id = user.id

        # create new Duty with user
        duty = Duty.objects.create(user=user) # auto save

        # verify duty count increases by 1
        self.assertEqual(Duty.objects.count(), 1)

        # verify duty's user information
        self.assertEqual(duty.user.name, name)
        self.assertEqual(duty.user.email, email)

        # deletion of duty
        duty.delete()

        user = User.objects.get(pk=user_id)

        # expect duty to be deleted, hence DoesNotExist must be raised
        with self.assertRaises(Duty.DoesNotExist):
            duty = user.duty


#############################################################################

class TestDutyManagerModel(BaseDutyTestCase):
    """Test Duty Manager model functionality"""

    def setUp(self):
        """Setup test data for Test Duty Manager model.
        """
        self.user1 = self.create_user()
        self.user2 = self.create_user()

    def test_duty_manager_basic_creation(self):
        """Ability to create duty manager as singleton.
        """
        # create 1st singleton manager
        duty_manager = DutyManager()

        # create 2nd singleton manager, verify it's the same instance with 1st
        duty_manager2 = DutyManager()
        self.assertIs(duty_manager, duty_manager2)
        self.assertIs(duty_manager2, DutyManager.instance)

    def test_start_and_clear_duty(self):
        """Duty manager can start duty if previously there is no duty
        then the duty can be cleared and replaced with newer one.
        """
        duty_manager = DutyManager()

        # verify initially no existing duty
        self.assertIsNone(duty_manager.duty)

        # start duty with auto_flush off
        duty_manager.start_duty(self.user1)

        # verify duty is started in duty manager
        self.assertIsNotNone(duty_manager.duty)
        self.assertIs(duty_manager.duty, self.user1.duty)
        self.assertIs(self.user1, duty_manager.user)

        # clear current duty
        duty_manager.force_fast_forward_duty(next_minutes=-1)
        duty_manager.clear_duty()

        # verify duty is cleared
        self.assertIsNone(duty_manager.duty)

        # expect duty to be deleted, hence DoesNotExist must be raised
        with self.assertRaises(Duty.DoesNotExist):
            self.user1.duty

    def test_only_one_active_duty_and_unable_clear_unfinished_duty(self):
        """One duty at a time handled by single manager. 
        New duty cannot be created when ongoing duty not finished yet.
        """
        duty_manager = DutyManager()

        # verify initially no existing duty
        self.assertIsNone(duty_manager.duty)

        # start 3 hour 1st duty with user1
        duty_manager.start_duty(self.user1)

        # verify duty started in duty manager
        self.assertIsNotNone(duty_manager.duty)

        # expect 2nd duty cannot be started since 
        # there is already an active one
        with self.assertRaises(CannotStartOverOngoingDuty):
            duty_manager.start_duty(self.user2)

        # expect 2nd duty not created, hence DoesNotExist must be raised
        with self.assertRaises(Duty.DoesNotExist):
            duty2 = self.user2.duty

        # expect 1st duty can't be cleared since
        # not finished yet
        with self.assertRaises(CannotClearUnfinishedDuty):
            duty_manager.clear_duty()

        # 1st duty remain active in duty manager
        self.assertIsNotNone(duty_manager.duty)

    def test_force_clear_ongoing_duty(self):
        """Force clean duty will cleanse ongoing duty. Hence duty manager 
        can re-create new duty over the previously ongoing one.
        """
        duty_manager = DutyManager()

        # verify initially no existing duty
        self.assertIsNone(duty_manager.duty)

        # start 3 hour 1st duty with user1
        duty_manager.start_duty(self.user1)

        # verify duty started in duty manager
        self.assertIsNotNone(duty_manager.duty)

        # force clear 1st duty
        duty_manager._clear()

        # # expect 1st duty to be deleted, hence DoesNotExist must be raised
        # with self.assertRaises(Duty.DoesNotExist):
        #     duty = self.user1.duty
        self.assertIsNone(duty_manager.duty)

        # enable to create new duty
        duty_manager.start_duty(self.user2)
        self.assertIsNotNone(duty_manager.duty)

        # verify duty created and relationship is still correct
        self.assertIs(duty_manager.duty, self.user2.duty)      

    def tearDown(self):
        # reset duty manager from any duty associated
        duty_manager = DutyManager()
        duty_manager.reset()



