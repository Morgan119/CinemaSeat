from django import forms


def detect_mobile_network(phone):
    if phone is None:
        return None

    cleaned = ''.join(ch for ch in str(phone).strip() if ch.isdigit())
    if cleaned.startswith('256'):
        cleaned = cleaned[3:]

    if cleaned.startswith(('077', '078')):
        return 'mtn'
    if cleaned.startswith(('070', '075', '076', '079')):
        return 'airtel'
    return None


class BookingForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
        ('card', 'Card'),
        ('cash', 'Pay at Entrance'),
    ])
    phone = forms.CharField(required=False)

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('payment_method')
        phone = (cleaned.get('phone') or '').strip()

        if method in ('mtn', 'airtel'):
            if not phone:
                self.add_error('phone', 'Enter a mobile money number.')
            else:
                network = detect_mobile_network(phone)
                if network != method:
                    self.add_error(
                        'phone',
                        f"This number is not registered with {'MTN' if method == 'mtn' else 'Airtel'}."
                    )

        return cleaned
