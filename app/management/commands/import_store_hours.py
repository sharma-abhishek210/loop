import csv
from datetime import datetime
from app.models import BusinessHours
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports data from CSV files'

# Import business hours data
    def handle(self, *args, **options):
        with open('business_hours.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader) 
            hours = []
            for row in reader:
                store_id, dayOfWeek, start_time_local, end_time_local = row
                hours.append(BusinessHours(
                    store_id=store_id,
                    dayOfWeek=int(dayOfWeek),
                    start_time_local=datetime.strptime(start_time_local, '%H:%M:%S').time(),
                    end_time_local=datetime.strptime(end_time_local, '%H:%M:%S').time(),
                ))
            BusinessHours.objects.bulk_create(hours)