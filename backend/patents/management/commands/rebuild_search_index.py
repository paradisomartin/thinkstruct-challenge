import json

from django.core.management.base import BaseCommand

from patents.services.indexing import rebuild_search_index


class Command(BaseCommand):
    help = "Rebuild all patent search vectors after ingestion (explicit, atomic)."

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(rebuild_search_index(), sort_keys=True))
