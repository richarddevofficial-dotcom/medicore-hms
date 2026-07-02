from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Patient
from staff.models import StaffProfile
from .serializers import PatientListSerializer, PatientDetailSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'phone', 'mrn']
    ordering_fields = ['created_at', 'first_name', 'mrn', 'status']
    ordering = ['-created_at']
    lookup_field = 'mrn'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientDetailSerializer
    
    def perform_create(self, serializer):
        from hospitals.models import Hospital
        serializer.save(hospital=Hospital.objects.first(), status='registered')
    
    @action(detail=True, methods=['post'])
    def assign_doctor(self, request, mrn=None):
        patient = self.get_object()
        doctor_id = request.data.get('assigned_doctor')
        try:
            doctor = StaffProfile.objects.get(id=doctor_id, role='doctor', is_active=True)
            patient.assigned_doctor = doctor
            patient.status = 'waiting'
            patient.save()
            return Response(PatientDetailSerializer(patient).data)
        except StaffProfile.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=404)
    
    @action(detail=True, methods=['post'])
    def request_lab_test(self, request, mrn=None):
        patient = self.get_object()
        lab_tests = request.data.get('lab_test_requested', '')
        if lab_tests:
            patient.lab_test_requested = lab_tests
            patient.status = 'lab_requested'
            patient.save()
        else:
            return Response({'error': 'No tests specified'}, status=400)
        return Response(PatientDetailSerializer(patient).data)
    
    @action(detail=True, methods=['post'])
    def start_lab_test(self, request, mrn=None):
        patient = self.get_object()
        patient.status = 'lab_in_progress'
        patient.save()
        return Response(PatientDetailSerializer(patient).data)
    
    @action(detail=True, methods=['post'])
    def submit_lab_results(self, request, mrn=None):
        patient = self.get_object()
        patient.lab_test_results = request.data.get('lab_test_results', '')
        patient.status = 'lab_completed'
        patient.save()
        return Response(PatientDetailSerializer(patient).data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, mrn=None):
        patient = self.get_object()
        new_status = request.data.get('status')
        if 'diagnosis' in request.data:
            patient.diagnosis = request.data.get('diagnosis', '')
        if 'treatment_plan' in request.data:
            patient.treatment_plan = request.data.get('treatment_plan', '')
        if 'prescription' in request.data:
            patient.prescription = request.data.get('prescription', '')
        if 'doctor_notes' in request.data:
            patient.doctor_notes = request.data.get('doctor_notes', '')
        if new_status:
            patient.status = new_status
        patient.save()
        return Response(PatientDetailSerializer(patient).data)
    
    @action(detail=False, methods=['get'])
    def doctor_queue(self, request):
        doctor_id = request.query_params.get('doctor_id')
        queryset = Patient.objects.filter(
            status__in=['waiting', 'in_consultation', 'lab_requested', 'lab_in_progress', 'lab_completed']
        )
        if doctor_id:
            queryset = queryset.filter(assigned_doctor_id=doctor_id)
        return Response(PatientListSerializer(queryset, many=True).data)
    
    @action(detail=False, methods=['get'])
    def lab_queue(self, request):
        patients = Patient.objects.filter(
            status__in=['lab_requested', 'lab_in_progress', 'lab_completed']
        )
        return Response(PatientListSerializer(patients, many=True).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        today = timezone.now().date()
        return Response({
            'total_patients': Patient.objects.count(),
            'active_patients': Patient.objects.filter(is_active=True).count(),
            'today_new': Patient.objects.filter(created_at__date=today).count(),
            'waiting': Patient.objects.filter(status='waiting').count(),
            'in_consultation': Patient.objects.filter(status='in_consultation').count(),
            'lab_requested': Patient.objects.filter(status__in=['lab_requested', 'lab_in_progress', 'lab_completed']).count(),
            'treated_today': Patient.objects.filter(status='treated', updated_at__date=today).count(),
        })
    @action(detail=True, methods=['get'])
    def billing_summary(self, request, mrn=None):
        """Get complete patient summary for billing"""
        patient = self.get_object()
        return Response({
            'patient': PatientDetailSerializer(patient).data,
            'consultation': {
                'doctor': patient.doctor_name,
                'diagnosis': patient.diagnosis,
                'treatment_plan': patient.treatment_plan,
                'prescription': patient.prescription,
                'doctor_notes': patient.doctor_notes,
                'fee': 500,  # Default consultation fee
            },
            'lab': {
                'requested': patient.lab_test_requested,
                'results': patient.lab_test_results,
                'status': patient.status,
                'fee': 300,  # Default lab fee
            },
            'medicine': {
                'prescription': patient.prescription,
                'fee': 200,  # Default medicine fee
            },
            'summary': {
                'total': 1000,  # consultation + lab + medicine
                'status': patient.status,
                'is_ready_for_billing': patient.status in ['treated', 'lab_completed'],
            }
        })