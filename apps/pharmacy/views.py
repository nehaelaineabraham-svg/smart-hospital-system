from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Medicine
from clinical.models import Prescription


@login_required
def pharmacy_desk(request):
    medicines = Medicine.objects.all().order_by('name')
    pending_prescriptions = Prescription.objects.filter(is_dispensed=False).select_related('patient', 'doctor', 'consultation').order_by('-created_at')
    dispensed_history = Prescription.objects.filter(is_dispensed=True).select_related('patient', 'doctor').order_by('-created_at')[:10]

    return render(request, 'pharmacy/desk.html', {
        'medicines': medicines,
        'pending_prescriptions': pending_prescriptions,
        'dispensed_history': dispensed_history,
    })


@login_required
def dispense_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Deduct medicine stock
    for item in prescription.items.all():
        med = item.medicine
        if med.stock_quantity >= item.quantity:
            med.stock_quantity -= item.quantity
        else:
            med.stock_quantity = 0
        med.save()

    prescription.is_dispensed = True
    prescription.save()

    messages.success(request, f"Prescription #{prescription.id} for {prescription.patient.full_name} dispensed and stock updated!")
    return redirect('pharmacy_desk')
