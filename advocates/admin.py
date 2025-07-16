from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import (
    ConsultancyService, ConsultancyDetail,
    CorporateService, CorporateDetail,
    DisputeService, DisputeDetail,
    PropertyService, PropertyDetail
)

# =====================
# Consultancy Services
# =====================
class ConsultancyDetailInline(admin.TabularInline):
    model = ConsultancyDetail
    extra = 1

@admin.register(ConsultancyService)
class ConsultancyServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ConsultancyDetailInline]

admin.site.register(ConsultancyDetail)

# =====================
# Corporate Services
# =====================
class CorporateDetailInline(admin.TabularInline):
    model = CorporateDetail
    extra = 1

@admin.register(CorporateService)
class CorporateServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CorporateDetailInline]

# =====================
# Dispute Resolution
# =====================
class DisputeDetailInline(admin.TabularInline):
    model = DisputeDetail
    extra = 1

@admin.register(DisputeService)
class DisputeServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DisputeDetailInline]

# =====================
# Property Services
# =====================
class PropertyDetailInline(admin.TabularInline):
    model = PropertyDetail
    extra = 1

@admin.register(PropertyService)
class PropertyServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyDetailInline]
>>>>>>> aec289d (SEO start)
