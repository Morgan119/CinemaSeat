# CinemaSeat Django Website

## Run the project

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open the website:

```text
http://127.0.0.1:8000/
```

## Django admin login

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

Credentials for the sample development database:

```text
Username: admin
Password: CinemaSeat@2026
```

Custom interactive dashboard:

```text
http://127.0.0.1:8000/admin/dashboard/
```

## Sample customer login

Customer login page:

```text
http://127.0.0.1:8000/login/
```

Sample account:

```text
Username: kananula
Email: morgan@gmail.com
Password: 1234567
```

This password is only for sample development use. Change it before production.

## Main URLs

- `/` - CinemaSeat homepage
- `/login/` - Customer login
- `/signup/` - Customer registration
- `/logout/` - Sign out
- `/admin/` - Django admin
- `/admin/dashboard/` - CinemaSeat admin dashboard
- `/movie/<movie_id>/` - Movie details
- `/movie/<movie_id>/book/` - Showtime and seat selection
- `/payment/` - Payment page
- `/api/movies/` - Movie JSON API

## Booking flow

1. Register or log in.
2. Select a movie from the homepage.
3. Select a showtime.
4. Select available seats.
5. Continue to payment.
6. Choose MTN Mobile Money, Airtel Money, card, or cash at cinema.
7. Confirm payment.
8. View the confirmation page and generated QR code.
