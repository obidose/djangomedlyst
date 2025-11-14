from django.contrib import admin
from .models import Patient, ConsultRequest, WardRound, Task


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'nhi_number', 'current_responsible_team', 'clerking_status', 'post_take_ward_round_status', 'datetime_of_arrival']
    list_filter = ['current_responsible_team', 'current_parent_specialty', 'clerking_status', 'post_take_ward_round_status', 'referral_source', 'admission_type']
    search_fields = ['name', 'nhi_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ConsultRequest)
class ConsultRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'specialty', 'status', 'requested_by', 'requested_at']
    list_filter = ['specialty', 'status']
    search_fields = ['patient__name', 'patient__nhi_number']


@admin.register(WardRound)
class WardRoundAdmin(admin.ModelAdmin):
    list_display = ['patient', 'ward_round_type', 'doctor', 'timestamp']
    list_filter = ['ward_round_type']
    search_fields = ['patient__name', 'patient__nhi_number', 'doctor']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['patient', 'description', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['priority', 'status']
    search_fields = ['patient__name', 'patient__nhi_number', 'description']
