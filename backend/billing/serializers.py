from rest_framework import serializers
from .models import Bill

class BillSerializer(serializers.ModelSerializer):
    insurance_company_name = serializers.CharField(source='insurance_company.name', read_only=True)
    
    class Meta:
        model = Bill
        fields = '__all__'
        read_only_fields = ['hospital', 'bill_number', 'total_amount', 'balance', 'created_at', 'updated_at']