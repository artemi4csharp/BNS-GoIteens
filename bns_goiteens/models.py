from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Avg
import datetime
from django.utils import timezone
from decimal import Decimal

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Номер телефона має бути в форматі '+999999999'. До 15 цифр"
)


class User(AbstractUser):
    bio = models.CharField(max_length=500, blank=True)
    phone = models.CharField(validators=[phone_validator], max_length=15)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")  # Додано дату народження

    def add_balance(self, amount):
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def is_birthday_today(self):
        if self.birth_date:
            today = timezone.now().date()
            return (self.birth_date.month == today.month and
                    self.birth_date.day == today.day)
        return False


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(verbose_name="Активно")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
    
    def __str__(self):
        return f"{self.name}"
    
        
class Location(models.Model):
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    
    
    class Meta:
        verbose_name = "Локація"
        verbose_name_plural = "Локації"

    def __str__(self):
        return f"{self.country}:{self.region or 'Немає'}:{self.city}"
    
    
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    
    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_type} #{self.object_id}"
    
    
class BaseOffer(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=1000, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.ForeignKey("Location", on_delete=models.PROTECT)
    image = models.ImageField(upload_to="items_image/", blank=True, null=True)

    class Meta:
        abstract = True


class Item(BaseOffer):
    
    def average_rating(self):
        content_type = ContentType.objects.get_for_model(self)
        avg_value = Rating.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).aggregate(avg=Avg("value"))["avg"]
        return round(avg_value or 0, 1)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return f'{self.name} - {self.category}'


class Service(BaseOffer):
    service_type = models.CharField(
        choices=[("offer", "Надаю"), ("request", "Шукаю")],
        default="offer"
    )
    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"

    def __str__(self):
        return f"{self.name} - {self.category}"
    
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="ratings")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинг"
        
        
    def __str__(self):
        return f"{self.content_object.name} - рейтинг:{self.value}"


class Promotion(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["-start_date"]
        
    def __str__(self):
        return f"{self.name} - active:{self.is_active}"
    
        
    def is_valid(self):
        return self.is_active and self.start_date <= now() <= self.end_date

class Discount(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="discounts")
    discount_type = models.CharField(max_length=10, choices=[("percent", "Процент"), ("fixed", "Фіксована")])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.promotion}, {self.discount_type}, {self.value}"

    def clean(self):
        if not self.item and not self.category:
            raise ValidationError("Discount must be linked to an item or category")
        
        
class SavedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_items")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Збережений об'єкт"
        verbose_name_plural = "Збережені об'єкти"
        unique_together = ("user", "content_type", "object_id")
        ordering = ["-saved_at"]
        
    def __str__(self):
        return f"{self.user.username}, {self.content_object}"

class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Написав {self.sender} до {self.receiver}"


class PromoCode(models.Model):
    PROMO_TYPE_CHOICES = [
        ('balance', 'Поповнення балансу'),
        ('discount', 'Знижка на замовлення'),
        ('free_item', 'Безкоштовний товар/велика знижка'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    promo_type = models.CharField(max_length=20, choices=PROMO_TYPE_CHOICES, verbose_name="Тип промокоду")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значення",
                                help_text="Сума поповнення або відсоток знижки")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    max_uses = models.PositiveIntegerField(default=1, verbose_name="Максимум використань")
    used_count = models.PositiveIntegerField(default=0, verbose_name="Використано разів")
    valid_from = models.DateTimeField(verbose_name="Діє з")
    valid_to = models.DateTimeField(verbose_name="Діє до")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    target_item = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Цільовий товар",
                                    help_text="Товар, на який діє промокод (для типу 'Безкоштовний товар')")
    target_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name="Цільова категорія",
                                        help_text="Категорія товарів, на які діє промокод (для типу 'Безкоштовний товар')")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоди"

    def __str__(self):
        return f"{self.code} ({self.get_promo_type_display()})"

    def is_valid(self):
        now = timezone.now()
        return (self.is_active and
                self.used_count < self.max_uses and
                self.valid_from <= now <= self.valid_to)

    def apply_promo(self, user, order_amount=None, item=None):
        if not self.is_valid():
            return {
                'success': False,
                'message': 'Промокод недійсний або закінчився'
            }

        result = {
            'success': True,
            'message': '',
            'new_amount': order_amount,
            'balance_added': 0,
            'item_discount': 0
        }

        if self.promo_type == 'balance':
            user.add_balance(self.value)
            self.used_count += 1
            self.save()
            result['balance_added'] = self.value
            result['message'] = f'Баланс поповнено на {self.value} грн'

        elif self.promo_type == 'discount':
            if order_amount:
                discount_amount = order_amount * (self.value / 100)
                result['new_amount'] = order_amount - discount_amount
                self.used_count += 1
                self.save()
                result['message'] = f'Знижка {self.value}% застосована. Знижка складає {discount_amount:.2f} грн'
            else:
                result['success'] = False
                result['message'] = 'Для цього типу промокоду потрібна сума замовлення'

        elif self.promo_type == 'free_item':
            if item and (self.target_item == item or
                         (self.target_category and item.category == self.target_category)):
                item_discount = item.price * Decimal('0.9')
                result['item_discount'] = item_discount
                self.used_count += 1
                self.save()
                result['message'] = f'Застосована знижка {item_discount:.2f} грн на товар {item.name}'
            elif not item:
                result['success'] = False
                result['message'] = 'Для цього типу промокоду потрібно вказати товар'
            else:
                result['success'] = False
                result['message'] = 'Промокод не дійсний для цього товару'

        return result
