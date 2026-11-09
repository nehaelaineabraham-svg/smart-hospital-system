from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from users import views as user_views
from opd import views as opd_views
from pharmacy import views as pharmacy_views
from billing import views as billing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root redirect
    path('', lambda request: redirect('dashboard'), name='home'),
    
    # Auth
    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),
    path('dashboard/', user_views.dashboard, name='dashboard'),

    # Smart Token Queue & OPD
    path('queue/display/', opd_views.queue_display, name='queue_display'),
    path('queue/display/<str:dept_code>/', opd_views.queue_display, name='queue_display_dept'),
    path('opd/book/', opd_views.register_patient_and_book, name='book_appointment'),
    path('doctor/call/<int:appointment_id>/', opd_views.call_next_patient, name='call_next_patient'),
    path('doctor/desk/<int:appointment_id>/', opd_views.doctor_consultation_desk, name='doctor_consultation_desk'),

    # Pharmacy
    path('pharmacy/', pharmacy_views.pharmacy_desk, name='pharmacy_desk'),
    path('pharmacy/dispense/<int:prescription_id>/', pharmacy_views.dispense_prescription, name='dispense_prescription'),

    # Billing
    path('billing/', billing_views.invoice_list, name='invoice_list'),
    path('billing/invoice/<int:invoice_id>/', billing_views.invoice_detail, name='invoice_detail'),
    path('billing/settle/<int:invoice_id>/', billing_views.settle_payment, name='settle_payment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
