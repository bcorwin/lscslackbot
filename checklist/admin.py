from django.contrib import admin
from models import Checklist, Task, assignedTask

# Register your models here.
# to do: filterable fields
# to do: make it so students can assign but not complete a task
# to do: students can only view their tasks
# to do: assignees can view their tasks and assigned to me
# to do: admins can view everything


class checklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'dmc_default', 'ia_default']


class assignedTaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'completed', 'assigned_to']


class myTask(assignedTask):
    class Meta:
        proxy = True


class myTaskAdmin(assignedTaskAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(user=request.user)


class assignedToMe(assignedTask):
    class Meta:
        verbose_name_plural = "Assigned to me"
        proxy = True


class assignedToMeAdmin(assignedTaskAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(assigned_to=request.user)

admin.site.register(Checklist, checklistAdmin)
admin.site.register(Task)
admin.site.register(assignedTask, assignedTaskAdmin)
admin.site.register(myTask, myTaskAdmin)
admin.site.register(assignedToMe, assignedToMeAdmin)
