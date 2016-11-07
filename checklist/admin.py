from django.contrib import admin
from models import Checklist, Task, assignedTask, Comment, Request, \
    assignedChecklist, approvalGroup

# to do: filterable fields
# to do: admins can view everything
# to do: check list maker group
# to do: reduce options in the admin user form


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

    def get_queryset(self, request):
        # only show your requests
        return self.model.objects.filter(assigned_to=request.user)

    def save_model(self, request, obj, form, change):
        obj.approved_by = request.user
        super(requestAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False


class taskInline(admin.TabularInline):
    model = Task
    extra = 1


class approvalGroupInline(admin.TabularInline):
    model = approvalGroup
    extra = 0


class assignedChecklistInline(admin.TabularInline):
    model = assignedChecklist
    extra = 0

    # Unable to have the cascade delete warning show (known django bug) so
    # remove ability and require deleting individual assignedTasks
    def has_delete_permission(self, request, obj=None):
        return False


class checklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'dmc_default', 'ia_default']
    inlines = [taskInline, assignedChecklistInline, approvalGroupInline]
    actions = [copy_checklist]


class requestInline(admin.TabularInline):
    model = Request
    fields = ['assigned_to']
    verbose_name_plural = "Request Approval"

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Only approved users can be requested based on approvalGroups
        if db_field.name == "assigned_to":
            obj_id = request.resolver_match.args[0]
            obj = assignedTask.objects.get(pk=obj_id)
            approved_users = obj.get_approved_users()
            # exclude logged in user
            approved_users = approved_users.exclude(pk=request.user.id)
            # exclude task user
            approved_users = approved_users.exclude(pk=obj.get_user().id)
            kwargs['queryset'] = approved_users
        return super(requestInline, self). \
            formfield_for_foreignkey(db_field, request, **kwargs)


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
    list_display = ['task', 'completed', 'awaiting_approval',
                    'get_user', 'approved_by']
    fields = list_display
    readonly_fields = fields
    inlines = [commentInline, addComment, requestInline]

    class Meta:
        verbose_name = 'My task'
        verbose_name_plural = 'My tasks'

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

    def get_queryset(self, request):
        # only show your tasks
        return self.model.objects.filter(assigned_checklist__user=request.user)

    def has_add_permission(self, request):
        return False


admin.site.register(Checklist, checklistAdmin)
admin.site.register(assignedTask, assignedTaskAdmin)
admin.site.register(Request, requestAdmin)
admin.site.register(assignedChecklist)
