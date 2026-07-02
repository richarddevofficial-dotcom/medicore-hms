from django.db import models
from hospitals.models import Hospital
from patients.models import Patient
from staff.models import StaffProfile

class Medicine(models.Model):
    FORM_CHOICES = [
        ('tablet', 'Tablet'), ('capsule', 'Capsule'), ('syrup', 'Syrup'),
        ('injection', 'Injection'), ('cream', 'Cream'), ('drops', 'Drops'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, default='General')
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='tablet')
    strength = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    def __str__(self):
        return f"{self.name} ({self.strength})" if self.strength else self.name


class Prescription(models.Model):
    STATUS = [
        ('pending', 'Pending Payment'),
        ('ready', 'Ready to Dispense'),
        ('dispensed', 'Dispensed'),
        ('partial', 'Partially Dispensed'),
        ('cancelled', 'Cancelled'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='pharmacy_prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, related_name='pharmacy_prescriptions')
    doctor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='pharmacy_prescriptions')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200)
    quantity_prescribed = models.IntegerField(default=1)
    quantity_dispensed = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dispensed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.medicine_name} - {self.status}"