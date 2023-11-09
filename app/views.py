from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import Report
from app.tasks import generate_report
import csv
from django.http import HttpResponse
import io
from io import StringIO

@api_view(['GET'])
def trigger_report(request):
    report = Report.objects.create()
    generate_report.delay(str(report.report_id))
    return Response({'report_id': str(report.report_id)}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_report(request, report_id):
    
    try:
        report = Report.objects.get(report_id=report_id)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

    if report.status == "Running":
        # If the report is not yet complete, return a "Running" status
        return Response({'status': 'Running'}, status=status.HTTP_200_OK)

    # If the report is complete, create a CSV file with the report data
    report_data = report.report_results
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week'])
    for data in report_data:
        writer.writerow([data['store_id'], data['uptime_last_hour'], data['uptime_last_day'], data['uptime_last_week'], data['downtime_last_hour'], data['downtime_last_day'], data['downtime_last_week']])

    response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    return response