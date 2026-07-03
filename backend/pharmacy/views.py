from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models as dj_models
from django.utils import timezone
from .models import Medicine, MedicineCategory, Prescription, StockMovement
from .serializers import MedicineSerializer, PrescriptionSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'generic_name', 'category__name']
    ordering_fields = ['name', 'quantity', 'expiry_date']
    
    def perform_create(self, serializer):
        from hospitals.models import Hospital
        serializer.save(hospital=Hospital.objects.first())
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Medicine.objects.count()
        low = Medicine.objects.filter(quantity__lte=dj_models.F('reorder_level')).count()
        critical = Medicine.objects.filter(quantity__lte=dj_models.F('min_stock')).count()
        return Response({'total': total, 'low_stock': low, 'critical': critical})

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['medicine_name', 'notes']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        from hospitals.models import Hospital
        serializer.save(hospital=Hospital.objects.first())
    
    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        prescription = self.get_object()
        qty = int(request.data.get('quantity', 0))
        if qty <= 0: return Response({'error': 'Invalid quantity'}, status=400)
        medicine = Medicine.objects.filter(name__iexact=prescription.medicine_name).first()
        if medicine:
            if medicine.quantity >= qty:
                medicine.quantity -= qty
                medicine.save()
            else:
                return Response({'error': f'Only {medicine.quantity} in stock'}, status=400)
        prescription.quantity_dispensed += qty
        prescription.status = 'dispensed' if prescription.quantity_dispensed >= prescription.quantity_prescribed else 'partial'
        prescription.dispensed_at = timezone.now()
        prescription.save()
        return Response(PrescriptionSerializer(prescription).data)
    
    @action(detail=False, methods=['get'])
    def queue(self, request):
        prescriptions = Prescription.objects.filter(status__in=['pending', 'ready', 'partial'])
        return Response(PrescriptionSerializer(prescriptions, many=True).data)
    
    @action(detail=False, methods=['post'])
    def mark_paid_by_patient(self, request):
        from patients.models import Patient
        mrn = request.data.get('mrn')
        if not mrn: return Response({'error': 'MRN required'}, status=400)
        try:
            patient = Patient.objects.get(mrn=mrn)
            count = Prescription.objects.filter(patient=patient, status='pending').update(status='ready')
            return Response({'message': f'{count} prescriptions marked as ready'})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)
