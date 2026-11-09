from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import uuid
import qrcode
import base64
from io import BytesIO
from .models import Ticket

METHODS = {
    'mtn': 'MTN Mobile Money',
    'airtel': 'Airtel Money',
    'card': 'Card payment',
    'cash': 'Cash at cinema',
}

def ticket_pdf(ticket):
    import fitz
    document = fitz.open()
    page = document.new_page(width=420, height=640)
    page.draw_rect(fitz.Rect(18, 18, 402, 622), color=(0.73, 0.15, 0.18), width=2)
    page.insert_text((36, 58), 'CINEMASEAT', fontsize=22, color=(0.73, 0.15, 0.18))
    page.insert_text((36, 82), 'Book your seat, enjoy the feat.', fontsize=10, color=(0.35, 0.32, 0.3))
    page.insert_text((36, 126), 'ADMIT ONE', fontsize=11, color=(0.45, 0.4, 0.36))
    page.insert_text((36, 156), ticket.movie[:34], fontsize=18, color=(0.12, 0.1, 0.09))
    details = [
        ('Reference', ticket.reference),
        ('Guest', ticket.customer_name),
        ('Showtime', ticket.show_time),
        ('Seats', ticket.seats),
        ('Payment', ticket.payment_method),
        ('Total', f'UGX {ticket.total:,}'),
        ('Cinema', 'Century Cinemax, Acacia Mall'),
    ]
    y = 196
    for label, value in details:
        page.insert_text((36, y), label.upper(), fontsize=8, color=(0.45, 0.4, 0.36))
        page.insert_text((130, y), str(value), fontsize=11, color=(0.12, 0.1, 0.09))
        y += 28
    qr = qrcode.make(ticket.qr_payload)
    image = BytesIO(); qr.save(image, format='PNG')
    page.insert_image(fitz.Rect(145, 430, 275, 560), stream=image.getvalue())
    page.insert_text((126, 582), 'Scan at the cinema entrance', fontsize=9, color=(0.35, 0.32, 0.3))
    response = HttpResponse(document.tobytes(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{ticket.reference}.pdf"'
    document.close()
    return response

def qr_image(payload):
    image = qrcode.make(payload)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()

@login_required(login_url='/login/')
def payment(request):
    movie = request.GET.get('movie') or request.POST.get('movie') or 'Selected movie'
    seats = request.GET.get('seats') or request.POST.get('seats') or ''
    show_time = request.GET.get('time') or request.POST.get('time') or '6:30 PM'
    if not seats:
        messages.error(request, 'Please select at least one seat.')
        return redirect('/')
    seat_list = [seat for seat in seats.split(',') if seat]
    total = len(seat_list) * 25000
    if request.method == 'POST':
        method = METHODS.get(request.POST.get('method'), 'MTN Mobile Money')
        reference = 'CS-' + uuid.uuid4().hex[:8].upper()
        payload = f'CINEMASEAT|{reference}|{movie}|{show_time}|{",".join(seat_list)}'
        ticket = Ticket.objects.create(
            reference=reference,
            customer_name=(request.user.get_full_name() or request.user.username),
            customer_username=request.user.username,
            movie=movie,
            show_time=show_time,
            seats=','.join(seat_list),
            total=total,
            payment_method=method,
            qr_payload=payload,
        )
        return render(request, 'cinemaseat/confirmation.html', {
            'movie': ticket.movie,
            'seat_list': seat_list,
            'total': ticket.total,
            'reference': ticket.reference,
            'show_time': ticket.show_time,
            'payment_method': ticket.payment_method,
            'qr_code': qr_image(ticket.qr_payload),
            'customer_name': ticket.customer_name,
            'issued': timezone.localtime(ticket.created_at),
        })
    return render(request, 'cinemaseat/payment.html', {
        'movie': movie,
        'seat_list': seat_list,
        'total': total,
        'show_time': show_time,
        'seats': ','.join(seat_list),
    })

@login_required(login_url='/login/')
def download_ticket(request, reference):
    ticket = get_object_or_404(Ticket, reference=reference, customer_username=request.user.username)
    return ticket_pdf(ticket)
