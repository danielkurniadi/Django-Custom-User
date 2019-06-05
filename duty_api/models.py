from datetime import datetime, timedelta
from django.db import models

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CannotStartOverOngoingDuty(Exception):
    def __init__(self):
        self.message = ("Existing duty is still ongoing and must be cleared first before"
            "starting new duty.")
        super().__init__(self.message)

class BehalfWithNoUserError(Exception):
    def __init__(self):
        self.message = ("Can't set behalf if no user that does duty on the specified behalf."
            "Set the user first.")
        super().__init__(self.message)

class CannotClearUnfinishedDuty(Exception):
    def __init__(self, duty_end=None):
        duty_end = "|UNKNOWN|" if not duty_end else "|{: %d %b %Y, %H:%M:%S}|".format(duty_end)
        self.message = ("Ongoing duty hasn't reach the duty end time. Either wait for"
            "duty to finish at %s or force clear." % duty_end)
        super().__init__(self.message)

class Duty(models.Model):
    # Task time constant (minutes)
    TASK_WINDOW = 30
    TASK1_MARK = 30 # from the start
    TASK2_MARK = 90 # from the start
    TASK3_MARK = 150

    # Duty Duration
    DUTY_DURATION = 180

    user = models.OneToOneField("users.User", null=True,
        on_delete=models.SET_NULL)
    
    _behalf = None

    duty_start = models.DateTimeField(editable=False)
    task1_start = models.DateTimeField(editable=False)
    task2_start = models.DateTimeField(editable=False)
    task3_start = models.DateTimeField(editable=False)

    duty_end =  models.DateTimeField(editable=False)
    task1_end = models.DateTimeField(editable=False)
    task2_end = models.DateTimeField(editable=False)
    task3_end = models.DateTimeField(editable=False)

    is_task1_submitted = models.BooleanField(default=False, null=False)
    is_task2_submitted = models.BooleanField(default=False, null=False)
    is_task3_submitted = models.BooleanField(default=False, null=False)

    ################################
    # User - Behalf
    ################################

    @property
    def behalf(self):
        if not hasattr(self, '_behalf'):
            self._behalf = None
        return self._behalf

    @behalf.setter
    def behalf(self, behalf_user):
        if not self.user:
            raise BehalfWithNoUserError
        self._behalf = behalf_user

    def __str__(self):
        if not self.user:
            return ("Zombie Duty Instance from time |{: %d %b %Y, %H:%M:%S}| to "
            "|{: %d %b %Y, %H:%M:%S}|".format(self.duty_start, self.duty_end))
        else:
            return ("Duty Instance from time |{: %d %b %Y, %H:%M:%S}| to "
            "|{: %d %b %Y, %H:%M:%S}| by {}".format(self.duty_start, self.duty_end, self.user.name))

    def save(self, *args, **kwargs):
        # Creation
        if not self.id:
            # Starting marker
            self.duty_start = timezone.now()
            self.task1_start = self.duty_start + timedelta(minutes=Duty.TASK1_MARK)
            self.task2_start = self.duty_start + timedelta(minutes=Duty.TASK2_MARK)
            self.task3_start = self.duty_start + timedelta(minutes=Duty.TASK3_MARK)
            # Ending marker
            self.duty_end = self.duty_start + timedelta(minutes=Duty.DUTY_DURATION)
            self.task1_end = self.task1_start + timedelta(minutes=Duty.TASK_WINDOW)
            self.task2_end = self.task2_start + timedelta(minutes=Duty.TASK_WINDOW)
            self.task3_end = self.task3_start + timedelta(minutes=Duty.TASK_WINDOW)

        return super(Duty, self).save(*args, **kwargs)

    def update_tasks_end(self, task1_end=None, task2_end=None, task3_end=None):
        self.task1_end = task1_end if not None else self.task1_end
        self.task2_end = task2_end if not None else self.task2_end
        self.task3_end = task3_end if not None else self.task3_end

    def update_duty_end(self, duty_end):
        if self.task1_end < duty_end:
            self.task1_end = duty_end
        if self.task2_end < duty_end:
            self.task2_end = duty_end
        if self.task3_end < duty_end:
            self.task3_end = duty_end
        
        self.duty_end = duty_end

##################################################################################

# Singleton
class DutyManager(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        else:
            cls.instance = object.__new__(cls, *args, **kwargs)
            return cls.instance

    @property
    def duty(self):
        if not hasattr(self, '_duty'):
            self._duty = None
        return self._duty

    @duty.setter
    def duty(self, new_duty):
        self._duty = new_duty

    @property
    def user(self):
        if not hasattr(self, '_duty'):
            self._duty = None
        if not self._duty:
            return None
        return self._duty.user

    ################################
    # Duty status
    ################################

    def is_duty_finished(self):
        return self.duty_end < timezone.now()

    ################################
    # Duty managements
    ################################

    def start_duty(self, user):
        if self.duty:
            raise CannotStartOverOngoingDuty
        self.duty = Duty.objects.create(user=user)

    def clear_duty(self):
        if self.duty.duty_end >= timezone.now():
            raise CannotClearUnfinishedDuty
        self._clear()

    def _clear(self):
        if self.duty:
            user = self.user
            self.duty.delete()

            user.duty = None
            user.save()
        
        self._duty = None

    def force_fast_forward_duty(self, next_minutes=0):
        if self.duty:
            nxt = timezone.now() + timedelta(minutes=next_minutes)
            self.duty.update_duty_end(nxt)

    def reset(self):
        # TODO: add more reset steps if necessary
        self._clear()


