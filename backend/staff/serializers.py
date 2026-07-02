from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StaffProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'name', 'hospital', 'department', 'department_name',
            'role', 'specialization', 'license_number', 'consultation_fee',
            'max_patients_per_day', 'phone', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['hospital', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None

class StaffCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = StaffProfile
        fields = [
            'first_name', 'last_name', 'email', 'password',
            'role', 'department', 'specialization', 'license_number',
            'consultation_fee', 'max_patients_per_day', 'phone'
        ]
    
    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        from hospitals.models import Hospital
        hospital = Hospital.objects.first()
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        
        staff = StaffProfile.objects.create(
            user=user,
            hospital=hospital,
            **validated_data
        )
        
        return staff