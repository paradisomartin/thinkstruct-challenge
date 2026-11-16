import json

from django.core.management.base import BaseCommand, CommandError

from patents.services.benchmark import benchmark_search


class Command(BaseCommand):
    help = "Measure warm filtered/unfiltered service calls on a stable indexed dataset."

    def add_arguments(self, parser):
        parser.add_argument("--repetitions", type=int, default=20)
        parser.add_argument("--warmups", type=int, default=3)
        parser.add_argument("--limit", type=int, default=20)

    def handle(self, *args, **options):
        try:
            report = benchmark_search(
                repetitions=options["repetitions"], warmups=options["warmups"],
                limit=options["limit"],
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(json.dumps(report, indent=2, sort_keys=True))
