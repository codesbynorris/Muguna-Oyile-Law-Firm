# advocates/management/commands/send_red_flag_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from advocates.models import ContactMessage, ScheduledCall
from advocates.views import send_html_email  # reuse your helper

class Command(BaseCommand):
    help = "Send reminders for unread messages and calls older than 48 hours"

    def handle(self, *args, **kwargs):
        time_limit = timezone.now() - timedelta(hours=48)

        # ---------------------------
        # Unread Contact Messages
        # ---------------------------
        messages_to_remind = ContactMessage.objects.filter(
            is_read=False,
            reminder_sent=False,
            created_at__lte=time_limit
        )

        for msg in messages_to_remind:
            # Send reminder email to admin
            send_html_email(
                subject=f"⚠️ Unread Contact Message: {msg.subject}",
                template="emails/contact_admin_reminder.html",
                context={"contact": msg, "firm_name": "Law Firm"},
                to_email=settings.CONTACT_RECEIVER_EMAIL,
            )
            msg.reminder_sent = True
            msg.save()
            self.stdout.write(self.style.SUCCESS(f"Reminder sent for message: {msg.subject}"))

        # ---------------------------
        # Unread Scheduled Calls
        # ---------------------------
        calls_to_remind = ScheduledCall.objects.filter(
            is_read=False,
            reminder_sent=False,
            created_at__lte=time_limit
        )

        for call in calls_to_remind:
            send_html_email(
                subject=f"⚠️ Unread Call Request: {call.subject}",
                template="emails/call_admin_reminder.html",
                context={"call": call, "firm_name": "Law Firm"},
                to_email=settings.CONTACT_RECEIVER_EMAIL,
            )
            call.reminder_sent = True
            call.save()
            self.stdout.write(self.style.SUCCESS(f"Reminder sent for call: {call.subject}"))

        self.stdout.write(self.style.SUCCESS("All reminders processed successfully."))
