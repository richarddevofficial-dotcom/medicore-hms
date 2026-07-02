from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from hospitals.views import HospitalViewSet
from patients.views import PatientViewSet
from staff.views import StaffViewSet
from departments.views import DepartmentViewSet
from rooms.views import WardViewSet, RoomViewSet, BedViewSet
from pharmacy.views import MedicineViewSet
from appointments.views import AppointmentViewSet
from billing.views import BillViewSet
from reports.views import dashboard_report
from pharmacy.views import PrescriptionViewSet
from insurance.views import InsuranceCompanyViewSet, InsuranceClaimViewSet
from reports.views import dashboard_report, staff_report, reception_report, cashier_report, pharmacy_report, lab_report

    
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email', '')
    phone = request.data.get('phone', '')
    password = request.data.get('password', '')
    
    from django.contrib.auth.models import User
    from staff.models import StaffProfile
    
    user = None
    if email:
        user = authenticate(username=email, password=password)
        if not user:
            u = User.objects.filter(email=email).first()
            if u: user = authenticate(username=u.username, password=password)
    if not user and phone:
        sp = StaffProfile.objects.filter(phone=phone).first()
        if sp: user = authenticate(username=sp.user.username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        staff = user.staff_profile
        return Response({
            'token': str(refresh.access_token),
            'user': {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'role': staff.role},
            'hospital': {'name': staff.hospital.name, 'slug': staff.hospital.slug}
        })
    return Response({'error': 'Invalid credentials'}, status=401)

router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'wards', WardViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'beds', BedViewSet)
router.register(r'medicines', MedicineViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'bills', BillViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'insurance-companies', InsuranceCompanyViewSet)
router.register(r'insurance-claims', InsuranceClaimViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/hospitals/login/', login_view, name='login'),
    path('api/v1/reports/dashboard/', dashboard_report, name='dashboard-report'),
    path('api/v1/', include(router.urls)),
    path('api/v1/reports/staff/', staff_report, name='staff-report'),
    path('api/v1/reports/reception/', reception_report, name='reception-report'),
    path('api/v1/reports/cashier/', cashier_report, name='cashier-report'),
    path('api/v1/reports/pharmacy/', pharmacy_report, name='pharmacy-report'),
    path('api/v1/reports/lab/', lab_report, name='lab-report'),
]
