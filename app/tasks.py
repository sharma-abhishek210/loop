from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import timedelta
from django.db.models import F
from app.models import StoreStatus, BusinessHours, StoreTimezone, Report
import csv
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from pytz import timezone

@shared_task
def generate_report(report_id):
    stores = StoreStatus.objects.values('store_id').distinct()
    report_data = []

    # Calculate uptime and downtime for each store
    for store in stores:
        store_id = store['store_id']

        print("store id: ", store_id)

        # Get the timezone of the store
        store_timezone_obj = StoreTimezone.objects.filter(store_id=store_id).first()
        if store_timezone_obj is not None:
            store_timezone = store_timezone_obj.timezone_str
        else:
            store_timezone = 'America/Chicago'

        # Convert the timezone string to a timezone object
        tz = timezone(store_timezone)

        statuses = StoreStatus.objects.filter(store_id=store_id).order_by('timestamp_utc')
        uptime_last_hour = uptime_last_day = uptime_last_week = 0
        downtime_last_hour = downtime_last_day = downtime_last_week = 0

        # Calculate uptime and downtime
        for i in range(len(statuses) - 1):
            duration = statuses[i+1].timestamp_utc - statuses[i].timestamp_utc

            start_time_local = statuses[i].timestamp_utc.astimezone(tz)
            end_time_local = statuses[i+1].timestamp_utc.astimezone(tz)

            # Check if the timestamps are within the store's business hours
            try:
                business_hours = BusinessHours.objects.get(store_id=store_id, dayOfWeek=start_time_local.weekday())
                if business_hours.start_time_local <= start_time_local.time() <= business_hours.end_time_local and \
                   business_hours.start_time_local <= end_time_local.time() <= business_hours.end_time_local:

                    if statuses[i].status == 'active':
                        uptime_last_hour += min(duration, timedelta(hours=1)).total_seconds() / 60
                        uptime_last_day += min(duration, timedelta(days=1)).total_seconds() / 3600
                        uptime_last_week += min(duration, timedelta(weeks=1)).total_seconds() / 3600
                    else:
                        downtime_last_hour += min(duration, timedelta(hours=1)).total_seconds() / 60
                        downtime_last_day += min(duration, timedelta(days=1)).total_seconds() / 3600
                        downtime_last_week += min(duration, timedelta(weeks=1)).total_seconds() / 3600
            except BusinessHours.DoesNotExist:
                # If there are no business hours for the store, it is open 24/7
                if statuses[i].status == 'active':
                    uptime_last_hour += min(duration, timedelta(hours=1)).total_seconds() / 60
                    uptime_last_day += min(duration, timedelta(days=1)).total_seconds() / 3600
                    uptime_last_week += min(duration, timedelta(weeks=1)).total_seconds() / 3600
                else:
                    downtime_last_hour += min(duration, timedelta(hours=1)).total_seconds() / 60
                    downtime_last_day += min(duration, timedelta(days=1)).total_seconds() / 3600
                    downtime_last_week += min(duration, timedelta(weeks=1)).total_seconds() / 3600

        # Add the store data to the report data
        report_data.append({
            'store_id': store_id,
            'uptime_last_hour': uptime_last_hour,
            'uptime_last_day': uptime_last_day,
            'uptime_last_week': uptime_last_week,
            'downtime_last_hour': downtime_last_hour,
            'downtime_last_day': downtime_last_day,
            'downtime_last_week': downtime_last_week,
        })

    # Update the report status
    report_status = Report.objects.get(report_id=report_id)
    report_status.status = 'Complete'
    report_status.report_results = report_data
    report_status.save()


@shared_task
def poll_store_status():
    with open('store_status.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        statuses = []
        for row in reader:
            store_id, status, timestamp_utc = row
            timestamp_utc = parse_timestamp(timestamp_utc)
            statuses.append(StoreStatus(
                store_id=store_id,
                timestamp_utc=timestamp_utc,
                status=status,
            ))
        print(row)
        print(store_id , " " , status, " " , timestamp_utc )
        StoreStatus.objects.bulk_create(statuses, 10000)

def parse_timestamp(timestamp_str):
    formats = ['%Y-%m-%d %H:%M:%S.%f %Z', '%Y-%m-%d %H:%M:%S %Z']
    for fmt in formats:
        try:
            return make_aware(datetime.strptime(timestamp_str, fmt))
        except ValueError:
            continue
       