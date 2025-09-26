from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, ScheduledCall, Category, Article

# -------------------------------
# Admin for Categories & Articles
# -------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "article_count")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "content", "author")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "subject", "created_at")
    search_fields = ("first_name", "last_name", "email", "subject")

# -------------------------------
# Admin for Scheduled Calls
# -------------------------------
@admin.register(ScheduledCall)
class ScheduledCallAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "date", "time_slot", "is_confirmed")
    list_filter = ("date", "is_confirmed")
    search_fields = ("first_name", "last_name", "email")
    actions = ["confirm_calls", "decline_calls"]

    # ✅ Confirm selected calls
    def confirm_calls(self, request, queryset):
        updated = 0
        for call in queryset:
            if not call.is_confirmed:
                call.is_confirmed = True
                call.save()
                updated += 1

                # Email to client: confirmed
                send_mail(
                    subject="✅ Your scheduled call has been confirmed",
                    message=(
                        f"Dear {call.first_name},\n\n"
                        f"Your scheduled call has been confirmed.\n"
                        f"- Date: {call.date}\n"
                        f"- Time: {call.time_slot}\n\n"
                        "Please add this to your calendar.\n\n"
                        "Best regards,\nLaw Firm Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[call.email],
                )

                # Email to admin: confirmation info
                send_mail(
                    subject=f"Call with {call.first_name} confirmed",
                    message=(
                        f"You confirmed the call request from {call.first_name} {call.last_name}.\n"
                        f"- Date: {call.date}\n"
                        f"- Time: {call.time_slot}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
                )

        self.message_user(request, f"{updated} call(s) confirmed and emails sent.", messages.SUCCESS)

    confirm_calls.short_description = "✅ Confirm selected calls"

    # ❌ Decline selected calls
    def decline_calls(self, request, queryset):
        updated = 0
        for call in queryset:
            if not call.is_confirmed:
                call.is_confirmed = False
                call.save()
                updated += 1

                # Email to client: declined
                send_mail(
                    subject="❌ Your scheduled call could not be confirmed",
                    message=(
                        f"Dear {call.first_name},\n\n"
                        f"Unfortunately, we are unable to confirm your scheduled call.\n"
                        f"- Requested Date: {call.date}\n"
                        f"- Requested Time: {call.time_slot}\n\n"
                        "Please choose another convenient time and reschedule via our contact page.\n\n"
                        "Best regards,\nLaw Firm Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[call.email],
                )

                # Email to admin: declined
                send_mail(
                    subject=f"Call with {call.first_name} declined",
                    message=(
                        f"You declined the call request from {call.first_name} {call.last_name}.\n"
                        f"- Requested Date: {call.date}\n"
                        f"- Requested Time: {call.time_slot}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
                )

        self.message_user(request, f"{updated} call(s) declined and emails sent.", messages.WARNING)

    decline_calls.short_description = "❌ Decline selected calls"
