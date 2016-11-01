from django.contrib import admin
from models import Checklist, Task, assignedTask, Comment, Request

# to do: filterable fields
# to do: students can only view their tasks
# to do: assignees can view their tasks and assigned to me
# to do: admins can view everything


class taskInline(admin.TabularInline):
    model = Task
    extra = 1


class checklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'dmc_default', 'ia_default']
    inlines = [taskInline]


class requestInline(admin.TabularInline):
    model = Request
    fields = ['assigned_to']
    verbose_name_plural = "Request Approval"


class commentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'text', 'inserted_date']
    readonly_fields = fields

    def has_add_permission(self, request):
        return False


class addComment(admin.TabularInline):
    model = Comment
    extra = 1
    max_num = 1
    verbose_name_plural = "Add a Comment"
    fields = ['text']

    def has_change_permission(self, request, obj=None):
        return False


class assignedTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'completed', 'user',
                    'awaiting_approval', 'approved_by']
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
admin.site.register(Request)
