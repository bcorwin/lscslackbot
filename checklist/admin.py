from django.contrib import admin
from models import Checklist, Task, assignedTask, Comment, Request, \
    assignedChecklist

# to do: filterable fields
# to do: students can only view their tasks
# to do: assignees can view their tasks and assigned to me
# to do: admins can view everything
# to do: check list maker group
# to do: DMC Validators can validate DMCs, IA Validators can validate IAs
# to do: can't assign/validate to self
# to do: requestor and validator can't be the same
# to do: make it so deleting assignedChecklist gives warning about cascadge


def copy_checklist(modeladmin, request, queryset):
    for checklist in queryset:
        checklist.save()
        tasks = Task.objects.filter(checklist=checklist)

        checklist.pk = None
        checklist.name += " copy"
        checklist.save()
        for task in tasks:
            task.pk = None
            task.checklist = checklist
            task.save()


class requestAdmin(admin.ModelAdmin):
    list_display = ['task', 'requestor', 'assigned_to']
    readonly_fields = ['requestor', 'task', 'assigned_to']
    fields = ['task', 'requestor', 'assigned_to', 'comment', 'result']

    def save_model(self, request, obj, form, change):
        obj.approved_by = request.user
        super(requestAdmin, self).save_model(request, obj, form, change)


class taskInline(admin.TabularInline):
    model = Task
    extra = 1


class assignedChecklistInline(admin.TabularInline):
    model = assignedChecklist
    extra = 0


class checklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'dmc_default', 'ia_default']
    inlines = [taskInline, assignedChecklistInline]
    actions = [copy_checklist]


class requestInline(admin.TabularInline):
    model = Request
    fields = ['assigned_to']
    verbose_name_plural = "Request Approval"


class commentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'text', 'inserted_date']
    readonly_fields = fields
    ordering = ['inserted_date']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class addComment(admin.TabularInline):
    model = Comment
    extra = 1
    max_num = 1
    verbose_name_plural = "Add a Comment"
    fields = ['text']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class assignedTaskAdmin(admin.ModelAdmin):
    # to do: add user from assigned checklist
    list_display = ['task', 'completed', 'awaiting_approval', 'approved_by']
    fields = list_display
    readonly_fields = fields
    inlines = [commentInline, addComment, requestInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comment):
                instance.user = request.user
                instance.save()
            if isinstance(instance, Request):
                instance.requestor = request.user
                instance.save()
        super(assignedTaskAdmin, self). \
            save_formset(request, form, formset, change)

admin.site.register(Checklist, checklistAdmin)
admin.site.register(assignedTask, assignedTaskAdmin)
admin.site.register(Request, requestAdmin)
