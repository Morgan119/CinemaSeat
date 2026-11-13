import csv
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Cinema, Movie, Screen, Showtime, Ticket

def ensure_screen():
    cinema, _ = Cinema.objects.get_or_create(name='Century Cinemax', defaults={'location': 'Acacia Mall', 'address': 'Acacia Mall, Kampala', 'total_screens': 4})
    return Screen.objects.get_or_create(cinema=cinema, screen_number=4, defaults={'screen_type': 'standard', 'total_seats': 120})[0]

def period_counts():
    now = timezone.now()
    tickets = Ticket.objects.all()
    return {
        'today': tickets.filter(created_at__date=now.date()).count(),
        'week': tickets.filter(created_at__gte=now - timedelta(days=7)).count(),
        'month': tickets.filter(created_at__gte=now - timedelta(days=30)).count(),
    }

@staff_member_required(login_url='/admin/login/')
def dashboard(request):
    tickets = Ticket.objects.all()
    seats_sold = sum(len([seat for seat in ticket.seats.split(',') if seat]) for ticket in tickets)
    capacity = max(Movie.objects.count(), 1) * 120
    context = {
        **period_counts(),
        'revenue': tickets.aggregate(total=Sum('total'))['total'] or 0,
        'occupancy': round(seats_sold / capacity * 100, 1),
        'popular': tickets.values('movie').annotate(total=Count('id')).order_by('-total')[:5],
        'recent': tickets.order_by('-created_at')[:8],
        'movie_count': Movie.objects.count(),
    }
    return render(request, 'cinemaseat/dashboard.html', context)

@staff_member_required(login_url='/admin/login/')
def movies_admin(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id) if movie_id else Movie()
        if request.POST.get('delete') == '1' and movie_id:
            movie.delete()
            return redirect('admin_movies')
        movie.title = request.POST.get('title', '').strip()
        movie.description = request.POST.get('description', '').strip()
        movie.duration = request.POST.get('duration', '').strip()
        movie.genre = request.POST.get('genre', 'Drama').strip()
        movie.rating = request.POST.get('rating', 'PG-13').strip()
        movie.score = request.POST.get('score') or 8
        movie.director = request.POST.get('director', '').strip()
        movie.featured = bool(request.POST.get('featured'))
        upload = request.FILES.get('poster_file')
        if upload:
            movie.poster_file = upload
            movie.poster = movie.poster_file.url
        elif not movie.poster:
            movie.poster = '/static/cinemaseat/posters/wonka.webp'
        movie.save()
        if upload:
            movie.poster = movie.poster_file.url
            movie.save(update_fields=['poster'])
        return redirect('admin_movies')
    edit = Movie.objects.filter(id=request.GET.get('edit')).first()
    return render(request, 'cinemaseat/admin_movies.html', {'movies': Movie.objects.order_by('title'), 'edit': edit})

@staff_member_required(login_url='/admin/login/')
def showtimes_admin(request):
    if request.method == 'POST':
        showtime_id = request.POST.get('showtime_id')
        show = get_object_or_404(Showtime, id=showtime_id) if showtime_id else Showtime(screen=ensure_screen())
        if request.POST.get('delete') == '1' and showtime_id:
            show.delete()
            return redirect('admin_showtimes')
        show.movie = get_object_or_404(Movie, id=request.POST.get('movie'))
        show.screen = ensure_screen()
        show.show_date = request.POST.get('show_date')
        show.show_time = request.POST.get('show_time')
        show.price_standard = request.POST.get('price_standard') or 25000
        show.price_vip = request.POST.get('price_vip') or 35000
        show.is_active = bool(request.POST.get('is_active'))
        show.save()
        return redirect('admin_showtimes')
    return render(request, 'cinemaseat/admin_showtimes.html', {
        'showtimes': Showtime.objects.select_related('movie').order_by('show_date', 'show_time'),
        'movies': Movie.objects.order_by('title'),
        'edit': Showtime.objects.filter(id=request.GET.get('edit')).first(),
    })

@staff_member_required(login_url='/admin/login/')
def pricing_admin(request):
    if request.method == 'POST':
        for show in Showtime.objects.all():
            standard = request.POST.get(f'standard_{show.id}')
            vip = request.POST.get(f'vip_{show.id}')
            if standard: show.price_standard = standard
            if vip: show.price_vip = vip
            show.save(update_fields=['price_standard', 'price_vip'])
        return redirect('admin_pricing')
    return render(request, 'cinemaseat/admin_pricing.html', {'showtimes': Showtime.objects.select_related('movie')})

@staff_member_required(login_url='/admin/login/')
def bookings_admin(request):
    return render(request, 'cinemaseat/admin_bookings.html', {'tickets': Ticket.objects.order_by('-created_at')})

@staff_member_required(login_url='/admin/login/')
def reports_admin(request):
    counts = period_counts()
    tickets = Ticket.objects.all()
    methods = tickets.values('payment_method').annotate(
        booking_count=Count('id'),
        total=Count('id'),
        revenue=Sum('total'),
    )
    movies = tickets.values('movie').annotate(
        booking_count=Count('id'),
        total=Count('id'),
        revenue=Sum('total'),
    ).order_by('-revenue')
    if request.GET.get('download') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cinemaseat-report-summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Report Type', 'Name', 'Booking Count', 'Revenue'])
        for item in methods:
            writer.writerow(['Payment Method', item['payment_method'], item['booking_count'], item['revenue'] or 0])
        writer.writerow([])
        for item in movies:
            writer.writerow(['Movie', item['movie'], item['booking_count'], item['revenue'] or 0])
        return response
    return render(request, 'cinemaseat/admin_reports.html', {
        **counts,
        'revenue': tickets.aggregate(total=Sum('total'))['total'] or 0,
        'methods': methods,
        'movies': movies,
    })
