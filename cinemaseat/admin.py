from django.contrib import admin
from .models import *

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title','genre','duration','rating','score','is_now_showing','featured')
    list_filter = ('genre','is_now_showing','is_coming_soon','featured','rating')
    search_fields = ('title','genre','description')
    list_editable = ('featured','is_now_showing')

@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name','location','total_screens'); search_fields = ('name','location')

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ('cinema','screen_number','screen_type','total_seats'); list_filter = ('screen_type',)

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie','screen','show_date','show_time','price_standard','price_vip','is_active')
    list_filter = ('show_date','is_active'); search_fields = ('movie__title','screen__cinema__name')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('screen','row_label','seat_number','seat_type','is_available'); list_filter = ('seat_type','is_available')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name','email','phone','loyalty_points','created_at'); search_fields = ('full_name','email')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference','user','showtime','total_amount','payment_status','booking_status','booking_date')
    list_filter = ('payment_status','booking_status'); search_fields = ('booking_reference','user__email')

@admin.register(BookingSeat)
class BookingSeatAdmin(admin.ModelAdmin): list_display = ('booking','seat','price_paid')
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin): list_display = ('booking','payment_method','provider','amount','status','payment_date'); list_filter = ('status','payment_method')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin): list_display = ('movie','user','rating','created_at'); list_filter = ('rating',)
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin): list_display = ('code','discount_type','discount_value','valid_from','valid_until','current_uses'); search_fields = ('code',)
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('reference','movie','show_time','seats','payment_method','status','customer_name','created_at','scanned_at')
    list_filter = ('status','payment_method','show_time')
    search_fields = ('reference','movie','customer_name','customer_username','seats')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin): list_display = ('user','type','title','is_read','created_at'); list_filter = ('type','is_read')

admin.site.site_header = 'CinemaSeat Administration'
admin.site.site_title = 'CinemaSeat Admin'
admin.site.index_title = 'Manage CinemaSeat'
