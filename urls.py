from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views
from .auth_views import login_view, signup_view, logout_view
from .dashboard import dashboard, movies_admin, showtimes_admin, pricing_admin, bookings_admin, reports_admin
from .payment_views import payment, download_ticket
from .scan_views import scanner, scan_ticket
from .ai_views import ai_home, ai_api

urlpatterns = [
    # Authentication
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),

    # Admin dashboard
    path("admin/login/", login_view, name="admin_login"),
    path("admin/dashboard/", dashboard, name="admin_dashboard"),
    path("admin/movies/", movies_admin, name="admin_movies"),
    path("admin/showtimes/", showtimes_admin, name="admin_showtimes"),
    path("admin/pricing/", pricing_admin, name="admin_pricing"),
    path("admin/bookings/", bookings_admin, name="admin_bookings"),
    path("admin/reports/", reports_admin, name="admin_reports"),
    path("admin/", admin.site.urls),

    # Public website
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("movie/<int:movie_id>/book/", views.booking, name="booking"),

    # Payment and booking confirmation
    path("payment/", payment, name="payment"),
    path("ticket/<str:reference>.pdf", download_ticket, name="download_ticket"),
    path("scan/", scanner, name="scanner"),
    path("scan/check/", scan_ticket, name="scan_ticket"),
    path("ai/", ai_home, name="ai_home"),
    path("ai/ask/", ai_api, name="ai_api"),

    # Movie API
    path("api/movies/", views.movies_api, name="movies_api"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
