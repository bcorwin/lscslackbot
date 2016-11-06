from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# to do: add a list of group(s) to who can approve a task/checklist
# To do: function to email user when assigned a task
# To do: ability to sign in using slack/gmail
# To do: set up groups (DMCs, those that can approve DMCs,
#           those that can approve IAs, and Admins)
# To do: clean up admin page
# To do: Assigned to me view (with ability to add comments and approve/deny
# To do: My tasks view (with ability to assign them to users)
# to do: make it so students can assign but not complete a task


@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    if sender == Request and instance.get_result() == '':
        rq_text = "Deleting request for " + str(instance.assigned_to)
        instance.task.add_comment(text=rq_text, user=instance.requestor)


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
        assignments = assignedChecklist.objects.filter(checklist=self)
        users = set([task.get_user() for task in assignments])
        return users

    def add_task(self, task):
        assignments = assignedChecklist.objects.filter(checklist=self)
        for assign in assignments:
            assignedTask.objects.create(assigned_checklist=assign, task=task)

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
        self.checklist.add_task(self)

    def __str__(self):
        return self.text


class assignedChecklist(models.Model):
    '''
    A model to store which checklists are assigned to a user
    '''
    user = models.ForeignKey(User)
    checklist = models.ForeignKey(Checklist)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_user(self):
        return self.user

    def save(self, *args, **kwargs):
        super(assignedChecklist, self).save(*args, **kwargs)
        # when saving, create assignedTasks for that user
        tasks = Task.objects.filter(checklist=self.checklist)
        for task in tasks:
            assignedTask.objects.create(assigned_checklist=self, task=task)


class assignedTask(models.Model):
    '''
    A model to store tasks that have been assigned to a user
    '''
    assigned_checklist = models.ForeignKey(assignedChecklist)
    task = models.ForeignKey(Task)

    completed = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, related_name="approvedby",
                                    blank=True, null=True)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def awaiting_approval(self):
        try:
            self.request is None
            return True
        except:
            return False
    awaiting_approval.boolean = True

    def approve(self, user):
        self.completed = True
        self.approved_by = user
        self.save()
        self.add_comment(text="Approved", user=user)

    def deny(self, user):
        self.completed = False
        self.approved_by = None
        self.save()
        self.add_comment(text="Denied", user=user)

    def get_user(self):
        return self.assigned_checklist.get_user()
    get_user.short_description = 'User'

    def add_comment(self, text, user):
        comment = Comment(text=text, user=user, task=self)
        comment.save()

    def complete_task(self, approved_by):
        self.completed = True
        self.approved_by = approved_by
        self.save()

    def __str__(self):
        return str(self.task)


class Request(models.Model):
    '''
    A model to store requests
    '''
    task = models.OneToOneField('assignedTask')
    requestor = models.ForeignKey(User, related_name="requestor")
    assigned_to = models.ForeignKey(User,
                                    related_name="assigned_to")

    comment = models.TextField(max_length=1024, default='')
    result = models.CharField(max_length=1,
                              choices=(('A', 'Approve'), ('D', 'Deny')))
    approved_by = models.ForeignKey(User,
                                    related_name="approved_by",
                                    null=True, blank=True)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_result(self):
        return self.result

    def save(self, *args, **kwargs):
        if not self.pk:  # Only do this when creating a Request
            rq_text = "Requesting approval from " + str(self.assigned_to)
            self.task.add_comment(text=rq_text, user=self.requestor)
        else:
            orig = Request.objects.get(pk=self.pk)
            if orig.assigned_to != self.assigned_to:
                # If the assigned to person changes, make note of that
                rq_text = "Now requesting approval from " + \
                    str(self.assigned_to)
                self.task.add_comment(text=rq_text, user=self.requestor)
            elif self.comment != '':
                self.task.add_comment(text=self.comment, user=self.approved_by)
                if self.result == "A":
                    self.task.approve(self.approved_by)
                elif self.result == "D":
                    self.task.deny(self.approved_by)
                return self.delete()
        super(Request, self).save(*args, **kwargs)


class Comment(models.Model):
    '''
    A model to store comments
    '''
    text = models.TextField(max_length=1024)
    user = models.ForeignKey(User)
    task = models.ForeignKey(assignedTask)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Validator(models.Model):
    '''
    A model to store which admin groups can approve a checklist
    '''