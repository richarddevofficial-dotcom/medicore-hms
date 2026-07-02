from rest_framework.decorators import api_view
from rest_framework.response import Response
from patients.models import Patient
from billing.models import Bill
from staff.models import StaffProfile
from pharmacy.models import Medicine
from django.utils import timezone

@api_view(['GET'])
def dashboard_report(request):
    today = timezone.now().date()
    return Response({
        'patients': {
            'total': Patient.objects.count(),
            'new_today': Patient.objects.filter(created_at__date=today).count(),
        },
        'billing': {
            'total_bills': Bill.objects.count(),
            'paid': Bill.objects.filter(status='paid').count(),
            'total_revenue': sum(float(b.total_amount) for b in Bill.objects.filter(status='paid')),
        },
        'staff': {
            'total': StaffProfile.objects.count(),
            'doctors': StaffProfile.objects.filter(role='doctor').count(),
        },
        'pharmacy': {
            'total_medicines': Medicine.objects.count(),
            'low_stock': Medicine.objects.filter(quantity__lte=10).count(),
        },
    })
@api_view(['GET'])
def staff_report(request):
    """Report for doctors - patients treated"""
    from patients.models import Patient
    from django.utils import timezone
    today = timezone.now().date()
    
    return Response({
        'patients_treated_today': Patient.objects.filter(status='treated', updated_at__date=today).count(),
        'patients_waiting': Patient.objects.filter(status='waiting').count(),
        'total_patients': Patient.objects.count(),
        'generated_at': timezone.now().isoformat(),
        'role': 'doctor'
    })

@api_view(['GET'])
def reception_report(request):
    """Report for receptionists - patients registered"""
    from patients.models import Patient
    from django.utils import timezone
    today = timezone.now().date()
    
    return Response({
        'patients_registered_today': Patient.objects.filter(created_at__date=today).count(),
        'total_registered': Patient.objects.count(),
        'patients_waiting': Patient.objects.filter(status='waiting').count(),
        'generated_at': timezone.now().isoformat(),
        'role': 'receptionist'
    })

@api_view(['GET'])
def cashier_report(request):
    """Report for cashiers - bills and payments"""
    from billing.models import Bill
    from django.utils import timezone
    today = timezone.now().date()
    
    bills_today = Bill.objects.filter(created_at__date=today)
    
    return Response({
        'bills_created_today': bills_today.count(),
        'payments_today': bills_today.filter(status='paid').count(),
        'revenue_today': sum(float(b.total_amount or 0) for b in bills_today.filter(status='paid')),
        'pending_bills': Bill.objects.filter(status='pending').count(),
        'total_revenue': sum(float(b.total_amount or 0) for b in Bill.objects.filter(status='paid')),
        'generated_at': timezone.now().isoformat(),
        'role': 'cashier'
    })

@api_view(['GET'])
def pharmacy_report(request):
    """Report for pharmacists - medicines dispensed"""
    from pharmacy.models import Prescription
    from django.utils import timezone
    today = timezone.now().date()
    
    return Response({
        'dispensed_today': Prescription.objects.filter(status='dispensed', dispensed_at__date=today).count(),
        'pending': Prescription.objects.filter(status__in=['pending', 'ready']).count(),
        'total_dispensed': Prescription.objects.filter(status='dispensed').count(),
        'generated_at': timezone.now().isoformat(),
        'role': 'pharmacist'
    })

@api_view(['GET'])
def lab_report(request):
    """Report for lab technicians - tests performed"""
    from patients.models import Patient
    from django.utils import timezone
    today = timezone.now().date()
    
    return Response({
        'tests_completed_today': Patient.objects.filter(status='lab_completed', updated_at__date=today).count(),
        'tests_pending': Patient.objects.filter(status__in=['lab_requested', 'lab_in_progress']).count(),
        'total_tests': Patient.objects.filter(status='lab_completed').count(),
        'generated_at': timezone.now().isoformat(),
        'role': 'lab_technician'
    })
