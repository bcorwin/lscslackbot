from django.contrib import admin
from models import Checklist, Task

# Register your models here.


class checklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'dmc_default', 'ia_default']

admin.site.register(Checklist, checklistAdmin)
admin.site.register(Task)
