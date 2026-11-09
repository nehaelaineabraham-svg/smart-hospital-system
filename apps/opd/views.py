from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import datetime

from .models import Department, Doctor, Patient, Appointment
from clinical.models import Consultation, Prescription, PrescriptionItem, LabTestOrder
from pharmacy.models import Medicine
from billing.models import Invoice


def queue_display(request, dept_code=None):
    """
    Lobby / Reception TV Waiting Screen.
    Auto-updates to show who is currently being consulted and who is next.
    """
    today = datetime.date.today()
    departments = Department.objects.filter(is_active=True)
    
    selected_dept = None
    if dept_code:
        selected_dept = get_object_or_404(Department, code=dept_code)
        appointments = Appointment.objects.filter(department=selected_dept, appointment_date=today)
    else:
        appointments = Appointment.objects.filter(appointment_date=today)

    engaged_tokens = appointments.filter(status=Appointment.STATUS_ENGAGED).select_related('doctor', 'patient', 'department')
    waiting_tokens = appointments.filter(status__in=[Appointment.STATUS_IN_WAITING, Appointment.STATUS_CHECKED_IN]).select_related('doctor', 'patient', 'department').order_by('token_sequence')
    completed_tokens = appointments.filter(status=Appointment.STATUS_CONSULTED).select_related('doctor', 'patient')[:5]

    context = {
        'departments': departments,
        'selected_dept': selected_dept,
        'engaged_tokens': engaged_tokens,
        'waiting_tokens': waiting_tokens,
        'completed_tokens': completed_tokens,
        'today': today,
    }
    return render(request, 'opd/queue_display.html', context)


@login_required
def register_patient_and_book(request):
    """
    Front-Desk Receptionist booking or walk-in registration.
    """
    departments = Department.objects.filter(is_active=True)
    doctors = Doctor.objects.filter(is_available=True)
    today = datetime.date.today()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        contact = request.POST.get('contact')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        allergies = request.POST.get('allergies', '')
        
        doctor_id = request.POST.get('doctor_id')
        symptoms = request.POST.get('symptoms', '')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Check or create patient
        patient, _ = Patient.objects.get_or_create(
            contact_number=contact,
            defaults={
                'full_name': full_name,
                'dob': dob or '1995-01-01',
                'gender': gender or 'OTHER',
                'blood_group': blood_group,
                'medical_allergies': allergies,
            }
        )

        # Generate appointment & token
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            department=doctor.department,
            appointment_date=today,
            status=Appointment.STATUS_IN_WAITING,
            symptoms=symptoms
        )

        messages.success(request, f"Token #{appointment.token_number} issued for {patient.full_name}! Queued for {doctor}.")
        return redirect('dashboard')

    return render(request, 'opd/book_appointment.html', {
        'departments': departments,
        'doctors': doctors,
        'today': today,
    })


@login_required
def call_next_patient(request, appointment_id):
    """
    Doctor calls a patient into the cabin. Sets status to ENGAGED.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Check if there is already an engaged patient and mark them completed or handle
    engaged_prev = Appointment.objects.filter(doctor=appointment.doctor, status=Appointment.STATUS_ENGAGED)
    for prev in engaged_prev:
        prev.status = Appointment.STATUS_CONSULTED
        prev.save()

    appointment.status = Appointment.STATUS_ENGAGED
    appointment.save()

    messages.info(request, f"Now calling Token #{appointment.token_number}: {appointment.patient.full_name}")
    return redirect('doctor_consultation_desk', appointment_id=appointment.id)


@login_required
def doctor_consultation_desk(request, appointment_id):
    """
    Doctor's active consultation cabin workspace.
    Write clinical notes, record vitals, prescribe medicines with live stock check, order lab tests.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient = appointment.patient
    medicines = Medicine.objects.filter(is_active=True).order_by('name')

    # Get or create consultation record
    consultation, _ = Consultation.objects.get_or_create(
        appointment=appointment,
        defaults={
            'patient': patient,
            'doctor': appointment.doctor,
            'chief_complaints': appointment.symptoms or 'General consultation'
        }
    )

    if request.method == 'POST':
        # Vitals & Clinical notes
        consultation.blood_pressure = request.POST.get('blood_pressure', '')
        consultation.pulse_rate = request.POST.get('pulse_rate', '')
        consultation.temperature = request.POST.get('temperature', '')
        consultation.spo2 = request.POST.get('spo2', '')
        consultation.chief_complaints = request.POST.get('chief_complaints', '')
        consultation.diagnosis = request.POST.get('diagnosis', '')
        consultation.save()

        # Create Prescription if medicines added
        med_ids = request.POST.getlist('med_id')
        dosages = request.POST.getlist('dosage')
        durations = request.POST.getlist('duration')
        quantities = request.POST.getlist('quantity')

        if med_ids:
            rx, _ = Prescription.objects.get_or_create(
                consultation=consultation,
                defaults={'patient': patient, 'doctor': appointment.doctor}
            )
            rx.general_advice = request.POST.get('general_advice', '')
            rx.save()

            # Clear old items if re-saving
            rx.items.all().delete()
            pharmacy_charge = 0
            for i, med_id in enumerate(med_ids):
                if med_id:
                    med = Medicine.objects.get(id=med_id)
                    qty = int(quantities[i]) if i < len(quantities) and quantities[i] else 10
                    PrescriptionItem.objects.create(
                        prescription=rx,
                        medicine=med,
                        dosage=dosages[i] if i < len(dosages) else '1-0-1',
                        duration=durations[i] if i < len(durations) else '5 days',
                        quantity=qty,
                        instructions=request.POST.get(f'instructions_{i}', 'After meals')
                    )
                    pharmacy_charge += (med.unit_price * qty)

        # Lab Tests
        lab_test_name = request.POST.get('lab_test_name')
        lab_charge = 0
        if lab_test_name:
            LabTestOrder.objects.create(
                consultation=consultation,
                patient=patient,
                test_name=lab_test_name,
                price=350.00,
                status='ORDERED'
            )
            lab_charge = 350.00

        # Mark appointment as CONSULTED
        appointment.status = Appointment.STATUS_CONSULTED
        appointment.save()

        # Auto-generate or update Invoice
        inv, _ = Invoice.objects.get_or_create(
            appointment=appointment,
            defaults={'patient': patient}
        )
        inv.consultation_fee = appointment.doctor.consultation_fee
        if med_ids:
            inv.pharmacy_fee = pharmacy_charge
        if lab_test_name:
            inv.lab_fee += lab_charge
        inv.save()

        messages.success(request, f"Consultation for {patient.full_name} completed and bill generated!")
        return redirect('dashboard')

    past_consultations = Consultation.objects.filter(patient=patient).exclude(id=consultation.id).order_by('-created_at')

    return render(request, 'clinical/doctor_desk.html', {
        'appointment': appointment,
        'patient': patient,
        'consultation': consultation,
        'medicines': medicines,
        'past_consultations': past_consultations,
    })
