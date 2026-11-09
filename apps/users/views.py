from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F
import datetime

from users.models import User
from opd.models import Department, Doctor, Patient, Appointment
from pharmacy.models import Medicine
from clinical.models import Consultation, Prescription, PrescriptionItem, LabTestOrder
from billing.models import Invoice


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=uname, password=pwd)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()

    context = {
        'today': today,
    }

    # Role specific context
    if user.is_admin_user:
        context.update({
            'total_patients': Patient.objects.count(),
            'total_doctors': Doctor.objects.count(),
            'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
            'total_revenue': Invoice.objects.filter(payment_status='PAID').aggregate(Sum('net_payable'))['net_payable__sum'] or 0,
            'low_stock_medicines': Medicine.objects.filter(stock_quantity__lte=F('reorder_level')).count(),
            'recent_appointments': Appointment.objects.filter(appointment_date=today).order_by('-created_at')[:8],
            'departments': Department.objects.all(),
        })
    elif user.is_doctor:
        try:
            doc = user.doctor_profile
            today_apps = Appointment.objects.filter(doctor=doc, appointment_date=today).order_by('token_sequence')
            current_app = today_apps.filter(status=Appointment.STATUS_ENGAGED).first()
            waiting_apps = today_apps.filter(status__in=[Appointment.STATUS_IN_WAITING, Appointment.STATUS_CHECKED_IN])
            completed_apps = today_apps.filter(status=Appointment.STATUS_CONSULTED)
            context.update({
                'doctor': doc,
                'today_apps': today_apps,
                'current_app': current_app,
                'waiting_apps': waiting_apps,
                'completed_apps': completed_apps,
            })
        except Doctor.DoesNotExist:
            pass
    elif user.is_receptionist:
        context.update({
            'today_appointments': Appointment.objects.filter(appointment_date=today).order_by('token_sequence'),
            'departments': Department.objects.all(),
            'doctors': Doctor.objects.filter(is_available=True),
            'recent_patients': Patient.objects.order_by('-created_at')[:5],
        })
    elif user.is_pharmacist:
        context.update({
            'pending_prescriptions': Prescription.objects.filter(is_dispensed=False).order_by('-created_at'),
            'medicines': Medicine.objects.all().order_by('stock_quantity')[:10],
            'low_stock_count': Medicine.objects.filter(stock_quantity__lte=F('reorder_level')).count(),
        })
    elif user.is_lab_tech:
        context.update({
            'lab_orders': LabTestOrder.objects.all().order_by('-created_at'),
        })
    else: # Patient
        try:
            patient = user.patient_profile
            context.update({
                'patient': patient,
                'my_appointments': Appointment.objects.filter(patient=patient).order_by('-appointment_date'),
                'my_prescriptions': Prescription.objects.filter(patient=patient).order_by('-created_at'),
            })
        except:
            pass

    return render(request, 'dashboard.html', context)
