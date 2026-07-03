from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Hospital
from .serializers import HospitalSerializer, HospitalRegistrationSerializer

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HospitalRegistrationSerializer
        return HospitalSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hospital = serializer.save()
        return Response({
            'message': 'Hospital registered successfully',
            'hospital_id': hospital.id,
            'hospital_name': hospital.name,
        }, status=status.HTTP_201_CREATED)
    
   