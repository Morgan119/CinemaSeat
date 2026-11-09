from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Ticket

def find_ticket(raw):
    value = (raw or '').strip()
    if not value:
        return None
    if value.upper().startswith('CINEMASEAT|'):
        parts = value.split('|')
        if len(parts) > 1:
            value = parts[1]
    return Ticket.objects.filter(reference__iexact=value).first() or Ticket.objects.filter(qr_payload=raw.strip()).first()

@staff_member_required(login_url='/login/')
def scanner(request):
    recent = Ticket.objects.order_by('-created_at')[:8]
    return render(request, 'cinemaseat/scanner.html', {'recent': recent})

@staff_member_required(login_url='/login/')
@require_POST
def scan_ticket(request):
    ticket = find_ticket(request.POST.get('code', ''))
    if not ticket:
        return JsonResponse({'ok': False, 'status': 'invalid', 'message': 'Ticket not found. This QR code is not a CinemaSeat booking.'})
    if ticket.status == 'used':
        return JsonResponse({
            'ok': False,
            'status': 'used',
            'message': f'{ticket.reference} was already scanned at {timezone.localtime(ticket.scanned_at):%d %b %Y, %I:%M %p}.',
            'ticket': ticket_data(ticket),
        })
    ticket.status = 'used'
    ticket.scanned_at = timezone.now()
    ticket.scanned_by = request.user.username
    ticket.save(update_fields=['status', 'scanned_at', 'scanned_by'])
    return JsonResponse({
        'ok': True,
        'status': 'valid',
        'message': 'Ticket is valid. Entry granted and marked as used.',
        'ticket': ticket_data(ticket),
    })

def ticket_data(ticket):
    return {
        'reference': ticket.reference,
        'movie': ticket.movie,
        'time': ticket.show_time,
        'seats': ticket.seats,
        'customer': ticket.customer_name,
        'method': ticket.payment_method,
        'total': f'UGX {ticket.total:,}',
    }
