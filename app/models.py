from django.db import models
import uuid


class StoreStatus(models.Model):
    store_id = models.CharField(max_length=255)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)

class BusinessHours(models.Model):
    store_id = models.CharField(max_length=255)
    dayOfWeek = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()


class StoreTimezone(models.Model):
    store_id = models.CharField(max_length=255, null=True)
    timezone_str = models.CharField(max_length=50)

class Report(models.Model):
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, default='Running')
    report_results = models.JSONField(null=True, blank=True)