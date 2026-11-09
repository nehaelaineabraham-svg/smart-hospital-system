import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from opd.models import Department, Doctor, Patient, Appointment
from pharmacy.models import Medicine
from clinical.models import Consultation, Prescription, PrescriptionItem, LabTestOrder
from billing.models import Invoice

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds MediFlow with realistic demo data for departments, staff, doctors, medicines, and patients'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting MediFlow demo data seeding..."))

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mediflow.com',
                'first_name': 'Chief Medical',
                'last_name': 'Director',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write("Created Superuser: admin / admin123")

        # 2. Staff Roles
        staff_data = [
            ('reception', 'reception123', 'Aarti', 'Sharma', User.ROLE_RECEPTIONIST, 'reception@mediflow.com'),
            ('pharmacist', 'pharmacy123', 'Rohan', 'Kulkarni', User.ROLE_PHARMACIST, 'pharmacy@mediflow.com'),
            ('labtech', 'lab123', 'Sunita', 'Deshmukh', User.ROLE_LAB_TECH, 'lab@mediflow.com'),
        ]
        for uname, pwd, fn, ln, role, em in staff_data:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': fn, 'last_name': ln, 'role': role, 'email': em, 'is_staff': True}
            )
            if created:
                u.set_password(pwd)
                u.save()
                self.stdout.write(f"Created Staff: {uname} ({role})")

        # 3. Departments
        depts_info = [
            ('Cardiology', 'CARD', 2, 'Comprehensive cardiac care, angiography, and heart health.'),
            ('General Medicine', 'GEN', 1, 'Primary care, fever management, diabetes, and adult wellness.'),
            ('Neurology', 'NEUR', 2, 'Brain, spine, and central nervous system disorders.'),
            ('Orthopedics', 'ORTH', 1, 'Bone fractures, joint replacements, and sports injuries.'),
            ('Pediatrics', 'PED', 1, 'Child healthcare, vaccinations, and neonatal care.'),
            ('Dermatology', 'DERM', 3, 'Skin, hair, allergies, and cosmetic dermatology.')
        ]
        dept_objs = {}
        for name, code, floor, desc in depts_info:
            d, _ = Department.objects.get_or_create(name=name, defaults={'code': code, 'floor_number': floor, 'description': desc})
            dept_objs[code] = d

        # 4. Doctors
        doctors_info = [
            ('dr_jenkins', 'doctor123', 'Sarah', 'Jenkins', 'CARD', 'DM (Cardiology), MD', 'Consultant Cardiologist', 700.00, 'OPD-201'),
            ('dr_sharma', 'doctor123', 'Rajesh', 'Sharma', 'GEN', 'MD (Internal Medicine)', 'Senior Physician', 500.00, 'OPD-102'),
            ('dr_mehta', 'doctor123', 'Arun', 'Mehta', 'NEUR', 'MCh (Neurosurgery), MS', 'Chief Neurosurgeon', 850.00, 'OPD-205'),
            ('dr_patel', 'doctor123', 'Vikram', 'Patel', 'ORTH', 'MS (Orthopedics)', 'Orthopedic Specialist', 600.00, 'OPD-108'),
        ]
        doc_objs = {}
        for uname, pwd, fn, ln, dept_code, qual, spec, fee, room in doctors_info:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': fn, 'last_name': ln, 'role': User.ROLE_DOCTOR, 'email': f"{uname}@mediflow.com", 'is_staff': True}
            )
            u.set_password(pwd)
            u.save()
            doc, _ = Doctor.objects.get_or_create(
                user=u,
                defaults={
                    'department': dept_objs[dept_code],
                    'qualification': qual,
                    'specialization': spec,
                    'consultation_fee': fee,
                    'room_number': room,
                }
            )
            doc_objs[uname] = doc
            self.stdout.write(f"Created Doctor: Dr. {fn} {ln} [{dept_code}]")

        # 5. Pharmacy Medicines
        medicines_list = [
            ('Paracetamol 650mg', 'Acetaminophen', 'TABLET', 2.50, 450, 50),
            ('Amoxicillin 500mg', 'Amoxicillin Trihydrate', 'CAPSULE', 8.00, 180, 30),
            ('Atorvastatin 20mg', 'Atorvastatin Calcium', 'TABLET', 14.50, 120, 20),
            ('Metformin 500mg', 'Metformin Hydrochloride', 'TABLET', 4.00, 300, 40),
            ('Pantoprazole 40mg', 'Pantoprazole Sodium', 'TABLET', 7.50, 250, 30),
            ('Cetirizine 10mg', 'Cetirizine HCl', 'TABLET', 3.00, 200, 25),
            ('Cough Relief Expectorant', 'Ambroxol + Guaiphenesin', 'SYRUP', 85.00, 60, 15),
            ('Azithromycin 500mg', 'Azithromycin', 'TABLET', 22.00, 95, 20),
            ('Multivitamin & Zinc', 'Zincovit Multi-Nutrient', 'CAPSULE', 6.00, 350, 40),
        ]
        med_objs = []
        for name, gen, cat, price, qty, reorder in medicines_list:
            m, _ = Medicine.objects.get_or_create(
                name=name,
                defaults={
                    'generic_name': gen,
                    'category': cat,
                    'unit_price': price,
                    'stock_quantity': qty,
                    'reorder_level': reorder,
                    'expiry_date': datetime.date.today() + datetime.timedelta(days=365)
                }
            )
            med_objs.append(m)

        # 6. Patients
        patients_list = [
            ('Rahul Verma', datetime.date(1989, 5, 14), 'MALE', 'B+', '9876543210', 'Penicillin allergy'),
            ('Anita Roy', datetime.date(1995, 11, 20), 'FEMALE', 'O+', '9811223344', 'No known allergies'),
            ('Suresh Chandra', datetime.date(1965, 3, 10), 'MALE', 'A+', '9822334455', 'Diabetic, Sulfa drugs allergy'),
            ('Priya Nair', datetime.date(2001, 8, 25), 'FEMALE', 'AB+', '9833445566', 'Asthmatic'),
        ]
        patient_objs = []
        for fn, dob, gender, bg, phone, allergies in patients_list:
            p, _ = Patient.objects.get_or_create(
                full_name=fn,
                contact_number=phone,
                defaults={'dob': dob, 'gender': gender, 'blood_group': bg, 'medical_allergies': allergies, 'address': 'MG Road, City Center'}
            )
            patient_objs.append(p)
            self.stdout.write(f"Created Patient: {fn} (UHID: {p.uhid})")

        # 7. Appointments & Active Tokens for Today
        today = datetime.date.today()
        # Appointment 1: Engaged with Dr. Jenkins (Cardiology)
        app1, _ = Appointment.objects.get_or_create(
            patient=patient_objs[0],
            doctor=doc_objs['dr_jenkins'],
            department=dept_objs['CARD'],
            appointment_date=today,
            defaults={'status': Appointment.STATUS_ENGAGED, 'symptoms': 'Chest heaviness and mild palpitations.'}
        )

        # Appointment 2: In Waiting for Dr. Jenkins
        app2, _ = Appointment.objects.get_or_create(
            patient=patient_objs[1],
            doctor=doc_objs['dr_jenkins'],
            department=dept_objs['CARD'],
            appointment_date=today,
            defaults={'status': Appointment.STATUS_IN_WAITING, 'symptoms': 'Routine blood pressure checkup.'}
        )

        # Appointment 3: In Waiting for Dr. Sharma (General Medicine)
        app3, _ = Appointment.objects.get_or_create(
            patient=patient_objs[2],
            doctor=doc_objs['dr_sharma'],
            department=dept_objs['GEN'],
            appointment_date=today,
            defaults={'status': Appointment.STATUS_IN_WAITING, 'symptoms': 'High fever, body chills, and dry cough for 3 days.'}
        )

        # Appointment 4: Consulted earlier today
        app4, _ = Appointment.objects.get_or_create(
            patient=patient_objs[3],
            doctor=doc_objs['dr_patel'],
            department=dept_objs['ORTH'],
            appointment_date=today,
            defaults={'status': Appointment.STATUS_CONSULTED, 'symptoms': 'Right knee pain after sports workout.'}
        )

        # 8. Create Consultation, Prescription & Invoice for the completed appointment
        consult, _ = Consultation.objects.get_or_create(
            appointment=app4,
            defaults={
                'patient': app4.patient,
                'doctor': app4.doctor,
                'blood_pressure': '118/78 mmHg',
                'pulse_rate': '76 bpm',
                'temperature': '98.4 F',
                'spo2': '99%',
                'chief_complaints': 'Acute right knee pain, mild swelling after football match.',
                'clinical_findings': 'Tenderness on medial joint line, no visible deformity.',
                'diagnosis': 'Grade 1 Medial Collateral Ligament (MCL) Strain',
                'follow_up_date': today + datetime.timedelta(days=7),
            }
        )

        rx, _ = Prescription.objects.get_or_create(
            consultation=consult,
            defaults={
                'patient': app4.patient,
                'doctor': app4.doctor,
                'general_advice': 'RICE protocol (Rest, Ice, Compression, Elevation). Avoid heavy jogging for 10 days.',
                'is_dispensed': True
            }
        )
        PrescriptionItem.objects.get_or_create(
            prescription=rx,
            medicine=med_objs[0], # Paracetamol
            defaults={'dosage': '1-0-1', 'duration': '5 days', 'quantity': 10, 'instructions': 'Take after food for pain relief'}
        )

        # Lab test order
        LabTestOrder.objects.get_or_create(
            consultation=consult,
            patient=app4.patient,
            test_name='Knee Joint X-Ray (AP & Lateral)',
            defaults={'status': 'COMPLETED', 'findings': 'No fracture detected. Mild soft tissue inflammation.'}
        )

        # Final Consolidated Bill
        Invoice.objects.get_or_create(
            patient=app4.patient,
            appointment=app4,
            defaults={
                'consultation_fee': app4.doctor.consultation_fee,
                'pharmacy_fee': 25.00,
                'lab_fee': 450.00,
                'discount': 50.00,
                'payment_status': 'PAID',
                'payment_mode': 'UPI',
                'transaction_reference': 'UPI-REF-998822'
            }
        )

        self.stdout.write(self.style.SUCCESS("Demo database successfully initialized with all modules connected!"))
