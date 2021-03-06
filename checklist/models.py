from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# To do: function to email user when assigned a task
# To do: ability to sign in using slack/gmail
# To do: set up groups (DMCs, those that can approve DMCs,
#           those that can approve IAs, and Admins)
# bug: assigning a checklists to a user more than once doubles their tasks


@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    # Add a comment to an assigned task when deleting a request
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

    def get_approved_users(self):
        # Get a query set of users approved to validate this checklist
        approved_groups = approvalGroup.objects.filter(checklist=self)
        group_ids = [group.get_group().id for group in approved_groups]
        groups = Group.objects.filter(id__in=group_ids)
        approved_users = User.objects.filter(groups__in=groups)
        return approved_users

    def get_users(self):
        # Get a set of all users that have this checklist assigned to them
        assignments = assignedChecklist.objects.filter(checklist=self)
        users = set([task.get_user() for task in assignments])
        return users

    def add_task(self, task):
        # Add an assigned task object for a (new) task in a checklist
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

    def get_checklist(self):
        return self.checklist

    def save(self, *args, **kwargs):
        super(assignedChecklist, self).save(*args, **kwargs)
        # when saving, create assignedTasks for that user
        tasks = Task.objects.filter(checklist=self.checklist)
        for task in tasks:
            assignedTask.objects.create(assigned_checklist=self, task=task)

    def __str__(self):
        return str(self.checklist) + " is assigned to " + str(self.user)


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

    class Meta:
        verbose_name = "My Task"
        verbose_name_plural = "My Tasks"

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

    def get_approved_users(self):
        checklist = self.assigned_checklist.get_checklist()
        return checklist .get_approved_users()

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

    class Meta:
        verbose_name = "My Outstanding Request"
        verbose_name_plural = "My Outstanding Requests"

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

    def __str__(self):
        return str(self.requestor) + " is requesting approval from " + \
                str(self.assigned_to)


class Comment(models.Model):
    '''
    A model to store comments
    '''
    text = models.TextField(max_length=1024)
    user = models.ForeignKey(User)
    task = models.ForeignKey(assignedTask)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class approvalGroup(models.Model):
    '''
    A model to store which admin groups can approve a checklist
    '''
    checklist = models.ForeignKey(Checklist)
    group = models.ForeignKey(Group)

    inserted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_group(self):
        return self.group

    def __str__(self):
        return str(self.group) + " can approve " + str(self.checklist)
