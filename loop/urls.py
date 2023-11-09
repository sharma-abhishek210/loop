from django.contrib import admin
from django.urls import path
from app.views import trigger_report, get_report


urlpatterns = [
    path('admin/', admin.site.urls),
    path('trigger_report/', trigger_report),
    path('get_report/<uuid:report_id>/', get_report),

]