from django.contrib import admin
from .models import (
    ConsultancyService, ConsultancyDetail,
    CorporateService, CorporateDetail,
    DisputeService, DisputeDetail,
    PropertyService, PropertyDetail,
    ContactSubmission,
)

# =====================
# Base Inlines
# =====================
class BaseDetailInline(admin.TabularInline):
    model = None  # set dynamically
    extra = 1


# =====================
# Reusable Base Admin
# =====================
class BaseServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'published')
    list_editable = ('published',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'summary', 'meta_title', 'meta_description')
    list_filter = ('published',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'summary', 'icon', 'published')
        }),
        ('SEO Fields', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )
    inlines = []

# =====================
# Consultancy
# =====================
class ConsultancyDetailInline(BaseDetailInline):
    model = ConsultancyDetail

@admin.register(ConsultancyService)
class ConsultancyServiceAdmin(BaseServiceAdmin):
    inlines = [ConsultancyDetailInline]

# =====================
# Corporate
# =====================
class CorporateDetailInline(BaseDetailInline):
    model = CorporateDetail

@admin.register(CorporateService)
class CorporateServiceAdmin(BaseServiceAdmin):
    inlines = [CorporateDetailInline]

# =====================
# Dispute
# =====================
class DisputeDetailInline(BaseDetailInline):
    model = DisputeDetail

@admin.register(DisputeService)
class DisputeServiceAdmin(BaseServiceAdmin):
    inlines = [DisputeDetailInline]

# =====================
# Property
# =====================
class PropertyDetailInline(BaseDetailInline):
    model = PropertyDetail

@admin.register(PropertyService)
class PropertyServiceAdmin(BaseServiceAdmin):
    inlines = [PropertyDetailInline]

# =====================
# Contact Submissions
# =====================
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'ticket_id', 'timestamp')
    search_fields = ('name', 'email', 'subject', 'ticket_id')
    readonly_fields = ('timestamp', 'ip_address')
