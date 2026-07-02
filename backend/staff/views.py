from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StaffProfile
from .serializers import StaffSerializer, StaffCreateSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'department__name']
    ordering_fields = ['role', 'department', 'created_at']
    ordering = ['role', 'user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StaffCreateSerializer
        return StaffSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        staff = self.get_object()
        staff.is_active = not staff.is_active
        staff.save()
        return Response({
            'id': staff.id,
            'is_active': staff.is_active,
            'message': f'User {"activated" if staff.is_active else "deactivated"}'
        })
    
    @action(detail=True, methods=['post'])
    def update_role(self, request, pk=None):
        staff = self.get_object()
        new_role = request.data.get('role')
        valid_roles = [r[0] for r in StaffProfile.ROLES]
        if new_role not in valid_roles:
            return Response({'error': 'Invalid role'}, status=400)
        staff.role = new_role
        staff.save()
        return Response({
            'id': staff.id,
            'new_role': staff.get_role_display(),
            'message': f'Role updated to {staff.get_role_display()}'
        })
    
    @action(detail=False, methods=['get'])
    def doctors(self, request):
        doctors = StaffProfile.objects.filter(role='doctor', is_active=True)
        serializer = StaffSerializer(doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = StaffProfile.objects.count()
        doctors = StaffProfile.objects.filter(role='doctor').count()
        nurses = StaffProfile.objects.filter(role='nurse').count()
        active = StaffProfile.objects.filter(is_active=True).count()
        return Response({
            'total_staff': total,
            'doctors': doctors,
            'nurses': nurses,
            'active': active,
        })