from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from chat.models import ChatGroup


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        site = Site.objects.get(id=settings.SITE_ID)

        site.domain = settings.DOMAIN_NAME
        site.name = "ChatApp"

        site.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Site updated: {site.domain}"
            )
        )
        public_chat, created = ChatGroup.objects.get_or_create(
            group_name="public-chat",
            defaults={
                "title": "Global Community Chat",
                "is_private": False,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Created public-chat group"
                )
            )