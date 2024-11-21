from django.contrib import admin
from .models import UserProfile, Criterion, SubCriterion, Metrics, Document

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'start_date', 'end_date')

class CriterionAdmin(admin.ModelAdmin):
    list_display = ('criterionId', 'name', 'created_at', 'created_by')

class SubCriterionAdmin(admin.ModelAdmin):
    list_display = ('SubCriterionId', 'name', 'created_at', 'created_by', 'criterion')

class MetricsAdmin(admin.ModelAdmin):
    list_display = ('metricId', 'question', 'answer', 'max_length', 'answered_by', 'created_at', 'answered_at', 'created_by', 'sub_criterion')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('description', 'created_at', 'created_by', 'metrics')
    
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Criterion, CriterionAdmin)
admin.site.register(SubCriterion, SubCriterionAdmin)
admin.site.register(Metrics, MetricsAdmin)
admin.site.register(Document, DocumentAdmin)