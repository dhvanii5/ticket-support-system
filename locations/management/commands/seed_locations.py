"""
seed_locations management command — REMOVED.

Location data is no longer seeded from hardcoded values.
It is now fetched dynamically from the CountriesNow API
(https://countriesnow.space) via locations/services.py with
a 24-hour Django file-based cache.

No action needed — data loads automatically on first request.
To clear the cache manually, delete the .django_cache/ directory
at the project root.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "This command is obsolete. Location data now comes from CountriesNow API."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(
            "seed_locations is no longer needed.\n"
            "Location data is fetched live from countriesnow.space and cached for 24 hours.\n"
            "To pre-warm the cache, just hit /api/locations/countries/ once."
        ))