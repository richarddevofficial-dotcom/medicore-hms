from django.db import models
from hospitals.models import Hospital
from patients.models import Patient

class Bill(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('insurance', 'Insurance Claimed'),
        ('cancelled', 'Cancelled'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    bill_number = models.CharField(max_length=50, unique=True)
    patient_name = models.CharField(max_length=200)
    patient_mrn = models.CharField(max_length=50, blank=True)
    
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, default='cash')
    payment_date = models.DateField(null=True, blank=True)
    
    insurance_company = models.CharField(max_length=200, blank=True)
    insurance_policy = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            from datetime import datetime
            last = Bill.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{num:04d}"
        self.total_amount = self.consultation_fee + self.lab_fee + self.medicine_fee + self.room_fee + self.other_fee
        self.balance = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.bill_number
