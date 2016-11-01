from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# To do: function to assign a checklist to a user
# To do: function to assign a task to a user (email user when assigned?)?
# To do: ability to sign in using slack
# To do: set up groups (DMCs, those that can approve DMCs,
#           those that can approve IAs, and Admins)
# To do: clean up admin page
# To do: Assigned to me view (with ability to add comments and approve/deny
# To do: My tasks view (with ability to assign them to users)
# to do: ability to confirm/deny request and add comment
# to do: track changes (completed, assigned, etc.) and comments
# to do: for above, i'll probably need another model of outstanding items
#       assignedtaskid, view all comments together, confirm/deny option, save
#       this will then set completed = True for the assigned task


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
    approved_by = models.ForeignKey(User, related_name="approvedby",
                                    blank=True, null=True)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_user(self):
        return self.user

    def add_comment(self, text, author):
        comment = Comment(task=self,
                          text=text,
                          author=author)
        comment.save()

    def request_approval(self, assigned_to):
        request = Request(task=self, assigned_to=assigned_to)
        request.save()

    def complete_task(self, approved_by):
        self.completed = True
        self.approved_by = approved_by
        self.save()

    def __str__(self):
        return str(self.user) + ": " + str(self.task)


class Request(models.Model):
    '''
    A model to store requests
    '''
    task = models.OneToOneField('assignedTask')
    assigned_to = models.ForeignKey(User)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def approve(self, validator):
        self.task.complete_task(validator)
        ap_text = "Approved by " + str(validator)
        ap_comment = Comment(text=ap_text,
                             author=validator,
                             task=self.task)
        ap_comment.save()
        self.delete()

    def deny(self, validator):
        dy_text = "Request denied by " + str(validator)
        dy_comment = Comment(text=dy_text,
                             author=validator,
                             task=self.task)
        dy_comment.save()
        self.delete()

    def save(self, requestor, *args, **kwargs):
        if not self.pk:  # Only do this when creating a Request
            rq_text = "Requesting approval from " + str(self.assigned_to)
            request_comment = Comment(text=rq_text,
                                      author=requestor,
                                      task=self.task)
            request_comment.save()
        super(Checklist, self).save(*args, **kwargs)


class Comment(models.Model):
    '''
    A model to store comments
    '''
    text = models.CharField(max_length=1024)
    author = models.ForeignKey(User)
    task = models.ForeignKey(assignedTask)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
