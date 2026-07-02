from rest_framework import viewsets, filters
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['appointment_date', 'appointment_time', 'status']
    ordering = ['-appointment_date', '-appointment_time']
