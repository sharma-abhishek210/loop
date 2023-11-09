import csv
from datetime import datetime
from app.models import StoreTimezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports data from CSV files'
 # Import store timezone data

    def handle(self, *args, **options):
        with open('store_timezone.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)
            timezones = []
            for row in reader:
                store_id, timezone_str = row
                timezones.append(StoreTimezone(
                    store_id=store_id,
                    timezone_str=timezone_str,
                ))
            StoreTimezone.objects.bulk_create(timezones)
        