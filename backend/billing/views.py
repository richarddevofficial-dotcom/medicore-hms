from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
from .models import Bill
from .serializers import BillSerializer

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['bill_number', 'patient_name', 'status']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        from hospitals.models import Hospital
        serializer.save(hospital=Hospital.objects.first())
    
    @action(detail=True, methods=['post'])
    def make_payment(self, request, pk=None):
        bill = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        method = request.data.get('method', 'cash')
        
        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=400)
        
        bill.amount_paid = (bill.amount_paid or Decimal('0')) + amount
        bill.payment_method = method
        bill.payment_date = timezone.now().date()
        
        if bill.amount_paid >= (bill.total_amount or Decimal('0')):
            bill.status = 'paid'
        elif bill.amount_paid > 0:
            bill.status = 'partial'
        
        bill.save()
        return Response(BillSerializer(bill).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Bill.objects.count()
        paid = Bill.objects.filter(status='paid').count()
        pending = Bill.objects.filter(status='pending').count()
        revenue = sum(float(b.total_amount or 0) for b in Bill.objects.filter(status='paid'))
        return Response({'total_bills': total, 'paid': paid, 'pending': pending, 'revenue': revenue})