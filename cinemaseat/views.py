from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Movie, Ticket
DATA=[
('Black Panther: Wakanda Forever','Action','2h 41m','PG-13',7.2,'Queen Ramonda fights to protect Wakanda from intervening world powers as the nation mourns King T’Challa.','/static/cinemaseat/posters/black panther.webp',True),
('Oppenheimer','Drama','3h 00m','R',8.6,'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.','/static/cinemaseat/posters/oppenheimer.webp',True),
('Dune: Part Two','Sci-Fi','2h 46m','PG-13',8.7,'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.','/static/cinemaseat/posters/dune two.webp',False),
('Barbie','Comedy','1h 54m','PG-13',7.0,'Barbie suffers a crisis that leads her to travel to the real world.','/static/cinemaseat/posters/barbie.webp',False),
('Avatar: The Way of Water','Adventure','3h 12m','PG-13',7.6,'Jake Sully lives with his newfound family formed on the planet of Pandora.','/static/cinemaseat/posters/avatar.webp',False),
('Mission: Impossible — Dead Reckoning','Action','2h 43m','PG-13',7.7,'Ethan Hunt and his IMF team must track down a dangerous weapon.','/static/cinemaseat/posters/mission impossible.webp',False),
('Wonka','Family','1h 56m','PG',7.0,'A young chocolatier dreams of opening his own shop in a city famed for chocolate.','/static/cinemaseat/posters/wonka.webp',False),
('Kung Fu Panda 4','Animation','1h 34m','PG',6.3,'Po must train a new warrior when he becomes spiritual leader of the Valley of Peace.','/static/cinemaseat/posters/kungu fu panda 4.webp',False)]
def seed():
    if not Movie.objects.exists():
        for x in DATA: Movie.objects.create(title=x[0],genre=x[1],duration=x[2],rating=x[3],score=x[4],description=x[5],poster=x[6],featured=x[7])
@login_required(login_url='/login/')
def home(request):
    seed()
    initials = ''
    if request.user.is_authenticated:
        initials = (request.user.first_name or request.user.username)[:2].upper()
    return render(request, 'cinemaseat/home.html', {'movies': Movie.objects.all(), 'featured': Movie.objects.filter(featured=True).first(), 'user_initials': initials})
@login_required(login_url='/login/')
def movie_detail(request,movie_id): seed(); return render(request,'cinemaseat/detail.html',{'movie':get_object_or_404(Movie,id=movie_id)})
@login_required(login_url="/login/")
def booking(request,movie_id): seed(); return render(request,'cinemaseat/booking.html',{'movie':get_object_or_404(Movie,id=movie_id)})
@login_required(login_url='/login/')
def movies_api(request): seed(); return JsonResponse({'movies':list(Movie.objects.values())})

@login_required(login_url='/login/')
def profile(request):
    tickets = Ticket.objects.filter(customer_username=request.user.username)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('name', request.user.first_name).strip()
        request.user.email = request.POST.get('email', request.user.email).strip()
        request.user.save(update_fields=['first_name', 'email'])
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'cinemaseat/profile.html', {'tickets': tickets, 'booking_count': tickets.count(), 'spent': sum(ticket.total for ticket in tickets), 'user_initials': (request.user.first_name or request.user.username)[:2].upper()})

@login_required(login_url='/login/')
def my_bookings(request):
    tickets = Ticket.objects.filter(customer_username=request.user.username).order_by('-created_at')
    return render(request, 'cinemaseat/bookings.html', {'tickets': tickets, 'user_initials': (request.user.first_name or request.user.username)[:2].upper()})
