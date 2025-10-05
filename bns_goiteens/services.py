from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import PromoCode
import random
import string

User = get_user_model()


def generate_unique_code(length=8):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not PromoCode.objects.filter(code=code).exists():
            return code


def create_birthday_promos():
    today = timezone.now().date()
    users_with_birthday = User.objects.filter(
        birth_date__month=today.month,
        birth_date__day=today.day
    )

    created_promos = []
    for user in users_with_birthday:
        promo_code = PromoCode(
            code=f"BIRTHDAY_{generate_unique_code(6)}",
            promo_type='balance',
            value=50,
            is_active=True,
            max_uses=1,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=7),
        )
        promo_code.save()
        created_promos.append(promo_code)

        print(f"Створено промокод {promo_code.code} для користувача {user.username}")

    return created_promos


def calculate_cashback(amount):
    return amount * 0.03
