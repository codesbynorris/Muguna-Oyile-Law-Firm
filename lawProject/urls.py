from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.conf.urls import include

from advocates import views as main_views
from advocates import admin_views  # <-- now this works

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---------------------------

    # General Pages
    # ---------------------------
    path('', main_views.home, name='home'),
    path('about/', main_views.about, name='about'),
    path('team/', main_views.team, name='team'),
    path('contact/', main_views.contact_us, name='contact'),
    path('privacy-policy/', main_views.privacy_policy, name='privacy_policy'),
    path('terms-of-services/', main_views.terms_of_service, name='terms_of_service'),

    # ---------------------------
    # Articles
    # ---------------------------
    path('articles/', main_views.article_list, name='article_list'),
    path('articles/category/<slug:category_slug>/', main_views.article_list, name='article_by_category'),
    path('articles/<slug:slug>/', main_views.article_detail, name='article_detail'),

    # ---------------------------
    # Service Pages
    # ---------------------------
    path('intellectual-property/', main_views.intellectual_property, name='intellectual_property'),
    path('dispute-resolution/', main_views.dispute_resolution, name='dispute_resolution'),
    path('debt-management/', main_views.debt_management, name='debt_management'),
    path('commercial-practice/', main_views.commercial_practice, name='commercial_practice'),
    path('real-estate-leases/', main_views.real_estate_leases, name='real_estate_leases'),
    path('support-services/', main_views.support_services, name='support_services'),

    # ---------------------------
    # Admin Dashboard
    # ---------------------------
    path('admin-dashboard/', admin_views.dashboard_home, name='admin_dashboard_home'),
    path('admin-dashboard/contacts/', admin_views.contacts_list, name='admin_dashboard_contacts'),
    path('admin-dashboard/calls/', admin_views.scheduled_calls_list, name='admin_dashboard_calls'),
    path('admin-dashboard/activity/', admin_views.activity_log_list, name='admin_dashboard_activity'),

    # Call actions
    path('admin-dashboard/call/confirm/<int:call_id>/', admin_views.confirm_call, name='admin_confirm_call'),
    path('admin-dashboard/call/decline/<int:call_id>/', admin_views.decline_call, name='admin_decline_call'),

    # ---------------------------
    # Notifications
    # ---------------------------
    path('admin-dashboard/notifications/', admin_views.all_notifications, name='all_notifications'),
    path('admin-dashboard/notifications/fetch/', admin_views.fetch_notifications, name='fetch_notifications'),



    path('users/', include('users.urls')),

    # ✅ New Red Flag Messages
    path('admin-dashboard/red-flags/', admin_views.red_flag_messages, name='red_flag_messages'),

    # ✅ Fetch API for dropdown
    path('admin-dashboard/notifications/red-flags/', admin_views.fetch_notifications, name='fetch_red_flag_notifications'),

    # Calendar Events
    path('events/', main_views.fetch_events, name='fetch_events'),
    path('events/add/', main_views.add_event, name='add_event'),
    path('events/delete/<int:event_id>/', main_views.delete_event, name='delete_event'),
    path('events/edit/<int:event_id>/', main_views.edit_event, name='edit_event'),
]

# Serve robots.txt
urlpatterns += [
    re_path(r'^robots\.txt$', static_serve, {'path': 'robots.txt', 'document_root': settings.STATIC_ROOT}),
]

# Serve static & media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
