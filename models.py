from django.db import models

class User(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    password_hash = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    def __str__(self): return f'{self.full_name} ({self.email})'

class Movie(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    duration = models.CharField(max_length=20)
    genre = models.CharField(max_length=80)
    language = models.CharField(max_length=40, default='English')
    release_date = models.DateField(null=True, blank=True)
    poster = models.CharField(max_length=500)
    poster_file = models.ImageField(upload_to='posters/', blank=True, null=True)
    backdrop_url = models.CharField(max_length=500, blank=True)
    trailer_url = models.URLField(blank=True)
    rating = models.CharField(max_length=10, default='PG-13')
    score = models.DecimalField(max_digits=3, decimal_places=1, default=8.0)
    director = models.CharField(max_length=120, blank=True)
    cast = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    is_now_showing = models.BooleanField(default=True)
    is_coming_soon = models.BooleanField(default=False)
    def __str__(self): return self.title

class Cinema(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=30, blank=True)
    total_screens = models.PositiveIntegerField(default=1)
    def __str__(self): return f'{self.name} - {self.location}'

class Screen(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='screens')
    screen_number = models.PositiveIntegerField()
    screen_type = models.CharField(max_length=30, default='standard')
    total_seats = models.PositiveIntegerField(default=150)
    seat_layout = models.JSONField(default=dict, blank=True)
    def __str__(self): return f'{self.cinema.name} / Screen {self.screen_number}'

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_time = models.TimeField()
    price_standard = models.DecimalField(max_digits=10, decimal_places=2)
    price_vip = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f'{self.movie.title} - {self.show_date} {self.show_time}'

class Seat(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    row_label = models.CharField(max_length=3)
    seat_number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=20, default='standard')
    is_available = models.BooleanField(default=True)
    x_position = models.PositiveIntegerField(default=0)
    y_position = models.PositiveIntegerField(default=0)
    class Meta: unique_together = ('screen', 'row_label', 'seat_number')
    def __str__(self): return f'{self.screen} {self.row_label}{self.seat_number}'

class Booking(models.Model):
    booking_reference = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    showtime = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    booking_status = models.CharField(max_length=20, default='confirmed')
    qr_code_data = models.TextField(blank=True)
    def __str__(self): return self.booking_reference

class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_seats')
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta: unique_together = ('booking', 'seat')

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=30)
    provider = models.CharField(max_length=40, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: constraints = [models.UniqueConstraint(fields=('user','movie','booking'), name='one_review_per_booking')]

class PromoCode(models.Model):
    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_until = models.DateField()
    max_uses = models.PositiveIntegerField(default=0)
    current_uses = models.PositiveIntegerField(default=0)
    def __str__(self): return self.code

class Ticket(models.Model):
    reference = models.CharField(max_length=30, unique=True)
    customer_name = models.CharField(max_length=120)
    customer_username = models.CharField(max_length=150, blank=True)
    movie = models.CharField(max_length=180)
    show_time = models.CharField(max_length=40)
    seats = models.CharField(max_length=255)
    total = models.PositiveIntegerField(default=0)
    payment_method = models.CharField(max_length=40)
    qr_payload = models.TextField()
    status = models.CharField(max_length=20, default='valid')
    created_at = models.DateTimeField(auto_now_add=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.CharField(max_length=150, blank=True)
    def __str__(self): return f'{self.reference} · {self.movie}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_data = models.JSONField(default=dict, blank=True)
