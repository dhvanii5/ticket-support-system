from django.core.management.base import BaseCommand
from locations.models import Country, State, City

class Command(BaseCommand):
    help = 'Seed location data'

    def handle(self, *args, **kwargs):
        # India
        india = Country.objects.create(name='India', code='IN')
        gujarat = State.objects.create(name='Gujarat', country=india)
        State.objects.create(name='Maharashtra', country=india)
        State.objects.create(name='Karnataka', country=india)
        City.objects.create(name='Ahmedabad', state=gujarat)
        City.objects.create(name='Surat', state=gujarat)
        City.objects.create(name='Vadodara', state=gujarat)

        # USA
        usa = Country.objects.create(name='United States', code='US')
        california = State.objects.create(name='California', country=usa)
        State.objects.create(name='New York', country=usa)
        City.objects.create(name='Los Angeles', state=california)
        City.objects.create(name='San Francisco', state=california)

        # UK
        uk = Country.objects.create(name='United Kingdom', code='UK')
        england = State.objects.create(name='England', country=uk)
        City.objects.create(name='London', state=england)
        City.objects.create(name='Manchester', state=england)

        self.stdout.write(self.style.SUCCESS('Location data seeded!'))