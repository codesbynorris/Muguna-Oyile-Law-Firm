from django.core.management.base import BaseCommand
from advocates.models import CalendarEvent
from django.utils.timezone import localdate
from django.conf import settings
from advocates.views import send_html_email

class Command(BaseCommand):
    help = "Send email reminders for today's events"

    def handle(self, *args, **kwargs):
        today = localdate()
        events_today = CalendarEvent.objects.filter(date=today, reminder_sent=False)
        
        for event in events_today:
            # Send email to admin
            send_html_email(
                subject=f"Reminder: Event today - {event.title}",
                template="emails/event_reminder_admin.html",
                context={"event": event, "firm_name": "Law Firm"},
                to_email=settings.DEFAULT_FROM_EMAIL
            )

            # Optionally send to client (if client has email stored)
            # send_html_email(
            #     subject=f"Reminder: Your Event today - {event.title}",
            #     template="emails/event_reminder_client.html",
            #     context={"event": event, "firm_name": "Law Firm"},
            #     to_email=event.client_email
            # )

            event.reminder_sent = True
            event.save()

        self.stdout.write(self.style.SUCCESS(f"{events_today.count()} reminders sent."))
