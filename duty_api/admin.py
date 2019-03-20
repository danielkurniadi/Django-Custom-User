from django.contrib import admin
from .models import Duty

class DutyAdmin(admin.ModelAdmin):
    model = Duty

admin.site.register(Duty, DutyAdmin)
