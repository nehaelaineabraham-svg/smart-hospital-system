from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Invoice


@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('patient', 'appointment').order_by('-created_at')
    return render(request, 'billing/invoices.html', {
        'invoices': invoices,
    })


@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice.objects.select_related('patient', 'appointment'), id=invoice_id)
    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
    })


@login_required
def settle_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        mode = request.POST.get('payment_mode', 'CASH')
        ref = request.POST.get('transaction_ref', '')
        invoice.payment_mode = mode
        invoice.transaction_reference = ref
        invoice.payment_status = 'PAID'
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} marked as PAID via {mode}!")
    return redirect('invoice_detail', invoice_id=invoice.id)
