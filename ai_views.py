import json
import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import Movie, Ticket
from .film_intel import answer_intel, PLAYERS, FILMS
from .views import seed

MOODS = {
    'laugh': 'Comedy', 'funny': 'Comedy', 'fun': 'Comedy', 'family': 'Family',
    'kids': 'Family', 'child': 'Family', 'action': 'Action', 'fight': 'Action',
    'thriller': 'Action', 'serious': 'Drama', 'drama': 'Drama', 'think': 'Drama',
    'space': 'Sci-Fi', 'future': 'Sci-Fi', 'sci': 'Sci-Fi', 'adventure': 'Adventure',
    'animated': 'Animation', 'animation': 'Animation',
}

def movie_card(movie, reason):
    return {
        'id': movie.id,
        'title': movie.title,
        'genre': movie.genre,
        'score': str(movie.score),
        'duration': movie.duration,
        'poster': movie.poster,
        'reason': reason,
        'url': f'/movie/{movie.id}/',
    }

def recommend_for(text='', username=''):
    seed()
    movies = list(Movie.objects.all())
    wanted = set()
    lowered = text.lower()
    for word, genre in MOODS.items():
        if word in lowered:
            wanted.add(genre)
    history = Ticket.objects.filter(customer_username=username).order_by('-created_at')[:12]
    seen = {item.movie for item in history}
    for item in history:
        match = next((movie for movie in movies if movie.title == item.movie), None)
        if match:
            wanted.add(match.genre)
    ranked = sorted(movies, key=lambda movie: (
        movie.genre in wanted,
        float(movie.score),
        movie.featured,
    ), reverse=True)
    picks = []
    for movie in ranked:
        if movie.title in seen and len(ranked) > 3:
            continue
        reason = f'Matches your {movie.genre.lower()} mood.' if movie.genre in wanted else f'Highly rated at {movie.score}/10.'
        if any(item.movie != movie.title and Movie.objects.filter(title=item.movie, genre=movie.genre).exists() for item in history):
            reason = f'Because you booked other {movie.genre.lower()} films.'
        picks.append(movie_card(movie, reason))
        if len(picks) == 4:
            break
    return picks or [movie_card(movie, 'Popular now at CinemaSeat.') for movie in movies[:4]]

def smart_results(query):
    seed()
    words = [word for word in re.findall(r"[a-z0-9']+", query.lower()) if len(word) > 2]
    genres = {MOODS[word] for word in words if word in MOODS}
    found = []
    for movie in Movie.objects.all():
        haystack = f'{movie.title} {movie.genre} {movie.description} {movie.rating}'.lower()
        score = sum(3 for word in words if word in movie.title.lower())
        score += sum(1 for word in words if word in haystack)
        score += 2 if movie.genre in genres else 0
        if score:
            found.append((score, movie))
    found.sort(key=lambda item: (item[0], float(item[1].score)), reverse=True)
    return [movie_card(movie, f'{hits} matching signals · {movie.genre}') for hits, movie in found[:6]]

def assistant_reply(message, username):
    intel = answer_intel(message)
    if intel:
        return intel
    text = message.lower().strip()
    if any(word in text for word in ('pay', 'mtn', 'airtel', 'mobile money', 'payment')):
        return {
            'reply': 'At checkout, choose MTN Mobile Money or Airtel Money. Both are clickable. After payment, CinemaSeat prints a receipt and creates a scannable QR ticket.',
            'movies': [],
        }
    if any(word in text for word in ('time', 'showtime', 'seat', 'book')):
        return {
            'reply': 'Open a movie, click a showtime (12:00 PM, 3:15 PM, 6:30 PM, or 9:00 PM), choose your seats, then continue to payment. You must be signed in before booking.',
            'movies': recommend_for(text, username)[:2],
        }
    if any(word in text for word in ('recommend', 'suggest', 'watch', 'mood', 'what should')):
        picks = recommend_for(text, username)
        titles = ', '.join(movie['title'] for movie in picks[:3])
        return {'reply': f'Based on your request and booking history, I suggest: {titles}.', 'movies': picks}
    results = smart_results(text)
    if results:
        return {'reply': f'I found {len(results)} match{"es" if len(results) != 1 else ""}. Open one to choose a showtime.', 'movies': results}
    return {'reply': 'I can recommend a movie, find a title, explain showtimes, or guide you through MTN and Airtel payment.', 'movies': recommend_for('', username)[:3]}

@login_required(login_url='/login/')
def ai_home(request):
    picks = recommend_for(request.GET.get('mood', ''), request.user.username)
    return render(request, 'cinemaseat/ai.html', {'picks': picks})

@login_required(login_url='/login/')
@require_POST
def ai_api(request):
    try:
        body = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        body = request.POST
    kind = body.get('kind', 'assistant')
    text = body.get('text', '')
    if kind == 'search':
        return JsonResponse({'results': smart_results(text)})
    if kind == 'recommend':
        return JsonResponse({'results': recommend_for(text, request.user.username)})
    answer = assistant_reply(text, request.user.username)
    return JsonResponse(answer)
