from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


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