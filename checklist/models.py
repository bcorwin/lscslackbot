from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# To do: function to assign a checklist to a user
# To do: function to assign a task to a user (email user when assigned?)
# To do: ability to sign in using slack
# To do: set up groups (DMCs, those that can approve DMCs,
#           those that can approve IAs, and Admins)
# To do: clean up admin page
# To do: Assigned to me view (with ability to add comments and approve/deny
# To do: My tasks view (with ability to assign them to users)


class Checklist(models.Model):
    '''
    A model to store the names of checklists
    '''
    name = models.CharField(max_length=64, unique=True)
    dmc_default = models.BooleanField(default=False)
    ia_default = models.BooleanField(default=False)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_users(self):
        assigned_tasks = assignedTask.objects.filter(task__checklist=self)
        users = set([task.get_user() for task in assigned_tasks])
        return users

    def save(self, *args, **kwargs):
        # To do: Force at least one recrod to be default?
        # Only allow one record to be the default DMC checklist
        if self.dmc_default:
            try:
                temp = Checklist.objects.get(dmc_default=True)
                if self != temp:
                    temp.dmc_default = False
                    temp.save()
            except Checklist.DoesNotExist:
                pass

        # Only allow one record to be the default IA checklist
        if self.ia_default:
            try:
                temp = Checklist.objects.get(ia_default=True)
                if self != temp:
                    temp.ia_default = False
                    temp.save()
            except Checklist.DoesNotExist:
                pass

        super(Checklist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    '''
    A model to store the tasks in a check list
    '''
    checklist = models.ForeignKey(Checklist)
    text = models.CharField(max_length=128)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        # Add task to all users that have that checklist
        for user in self.checklist.get_users():
            assignedTask.objects.create(user=user, task=self)

    def __str__(self):
        return self.text


class assignedTask(models.Model):
    '''
    A model to store tasks that have been assigned to a user
    '''
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)

    completed = models.BooleanField(default=False)
    awaiting_feedback = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, blank=True,
                                    related_name='assignee')

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_user(self):
        return self.user

    def __str__(self):
        return str(self.user) + ": " + str(self.task)
