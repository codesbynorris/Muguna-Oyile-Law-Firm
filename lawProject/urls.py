from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.conf.urls import include

from advocates import views as main_views
from advocates import admin_views  # <-- now this works

app_name = 'articles'

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---------------------------

    # General Pages
    # ---------------------------
    path('', main_views.home, name='home'),
    path('users/', include('users.urls')),
    path('about/', main_views.about, name='about'),
    path('test/', main_views.test, name='test'),
    path('search/', main_views.search_articles, name='search_articles'),
    path('teams/', main_views.team, name='team'),
    path('contact/', main_views.contact_us, name='contact'),
    path('privacy-policy/', main_views.privacy_policy, name='privacy_policy'),
    path('terms-of-services/', main_views.terms_of_service, name='terms_of_service'),
    path('feedback/', main_views.feedback, name='feedback'),
    path('cookie-policy/', main_views.cookie_policy, name='cookie_policy'),

    # ---------------------------
    # Articles
    # ---------------------------
    path('articles/', main_views.article_list, name='article_list'),
    path('articles/category/<slug:category_slug>/', main_views.article_list, name='article_by_category'),
    path('articles/<slug:slug>/', main_views.article_detail, name='article_detail'),
    path("blogs/new/", admin_views.article_create, name="article_create"),

    path('manage-quotes/', admin_views.manage_quotes, name='manage_quotes'),
    path('quote/create/', admin_views.quote_create, name='quote_create'),
    path('quote/edit/<int:pk>/', admin_views.edit_quote, name='edit_quote'),
    path('quote/delete/<int:pk>/', admin_views.delete_quote, name='delete_quote'),

    # Calendar
    path('events/', admin_views.get_events, name='get_events'),
    path('events/add/', admin_views.add_event, name='add_event'),
    path('events/edit/<int:event_id>/', admin_views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', admin_views.delete_event, name='delete_event'),


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
    path('admin-dashboard/analytics/', admin_views.analytics_dashboard, name='analytics_dashboard'),
    path('admin-dashboard/contacts/', admin_views.contacts_list, name='admin_dashboard_contacts'),
    path('admin-dashboard/calls/', admin_views.scheduled_calls_admin, name='admin_dashboard_calls'),
    path('admin-dashboard/activity/', admin_views.activity_log_list, name='admin_dashboard_activity'),
    path("admin-dashboard/feedback/", admin_views.feedback_dashboard, name="feedback_page"),
    path('admin/scheduled-calls/<int:call_id>/mark-read/', admin_views.mark_call_read, name='mark_call_read'),


    # Call actions
    path('admin-dashboard/call/confirm/<int:call_id>/', admin_views.confirm_call, name='admin_confirm_call'),
    path('admin-dashboard/call/decline/<int:call_id>/', admin_views.decline_call, name='admin_decline_call'),

    path('test-email/', admin_views.test_email, name='test_email'),

    #Team Pages
    path('team/', main_views.team, name='team'),

    # ---------------------------
    # Notifications
    # ---------------------------
    path('admin-dashboard/notifications/', admin_views.all_notifications, name='all_notifications'),
    path('admin-dashboard/notifications/fetch/', admin_views.fetch_notifications, name='fetch_notifications'),

    # Admin dashboard blog management
    path('blogs/new/', admin_views.article_create, name='article_create'),  # create new blog
    path('admin-dashboard/blogs/', admin_views.manage_blogs, name='manage_blogs'),
    path('admin-dashboard/blogs/view/<int:blog_id>/', admin_views.view_blog, name='view_blog'),
    path('admin-dashboard/blogs/edit/<int:blog_id>/', admin_views.edit_blog, name='edit_blog'),
    path('admin-dashboard/blogs/delete/<int:blog_id>/', admin_views.delete_blog, name='delete_blog'),
    path('profile/', admin_views.admin_profile, name='admin_profile'),  # ✅ Add this
    path('logout/', admin_views.logout_view, name='logout'),


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

    path('messages/add/', admin_views.add_message, name='add_message'),
    path('calls/add/', admin_views.add_call, name='add_call'),

    path('profile/', admin_views.admin_profile, name='profile_settings'),
]

# Serve robots.txt
urlpatterns += [
    re_path(r'^robots\.txt$', static_serve, {'path': 'robots.txt', 'document_root': settings.STATIC_ROOT}),
]

# Serve static & media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
