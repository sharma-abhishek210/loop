import csv
from datetime import datetime
from django.utils.timezone import make_aware
from app.models import StoreStatus
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports data from CSV files'

    def parse_timestamp(self, timestamp_str):
        formats = ['%Y-%m-%d %H:%M:%S.%f %Z', '%Y-%m-%d %H:%M:%S %Z']
        for fmt in formats:
            try:
                return make_aware(datetime.strptime(timestamp_str, fmt))
            except ValueError:
                continue
        raise ValueError(f'time data {timestamp_str} does not match any valid format')

    def handle(self, *args, **options):
        # Import store data
        with open('store_status.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader) 
            statuses = []
            for row in reader:
                store_id, status, timestamp_utc = row
                timestamp_utc = self.parse_timestamp(timestamp_utc)
                statuses.append(StoreStatus(
                    store_id=store_id,
                    timestamp_utc=timestamp_utc,
                    status=status,
                ))
            print(row)
            print(store_id , " " , status, " " , timestamp_utc )
            StoreStatus.objects.bulk_create(statuses, 10000)