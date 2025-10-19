from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Avg
from django.utils import timezone
from decimal import Decimal
from django.utils.text import slugify
import uuid

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Номер телефона має бути в форматі '+999999999'. До 15 цифр"
)


class User(AbstractUser):
    bio = models.CharField(max_length=500, blank=True)
    phone = models.CharField(validators=[phone_validator], max_length=15)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    income = models.DecimalField(null=True, max_digits=10, decimal_places=2, default=0.00)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    ROLE_CHOICES = [
        ('admin', 'Адміністратор'),
        ('support', 'Служба підтримки'),
        ('promo', 'Промо-адміністратор'),
        ('user', 'Звичайний користувач'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def is_admin(self):
        return self.role == 'admin'

    def is_support(self):
        return self.role in ['admin', 'support']

    def is_promo_admin(self):
        return self.role in ['admin', 'promo']

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
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            i = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CategoryRequest(models.Model):
    STATUS_PENDING = 'P'
    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'В очікуванні'),
        (STATUS_APPROVED, 'Підтверджено'),
        (STATUS_REJECTED, 'Відхилено'),
    ]

    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        Category, null=True, blank=True, related_name='requested_children', on_delete=models.SET_NULL
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='category_requests')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_category_requests')

    class Meta:
        verbose_name = "Запит на категорію"
        verbose_name_plural = "Запити на категорію"
        ordering = ['-created_at']

    def approve(self, processed_by=None):
        """Створює Category і відмічає request як approved."""
        if self.status == self.STATUS_APPROVED:
            return None
        category = Category.objects.create(
            name=self.name,
            parent=self.parent,
            created_by=self.user
        )
        self.status = self.STATUS_APPROVED
        self.processed_at = timezone.now()
        self.processed_by = processed_by
        self.save()
        return category

    def reject(self, reason=None, processed_by=None):
        self.status = self.STATUS_REJECTED
        if reason:
            self.admin_comment = reason
        self.processed_at = timezone.now()
        self.processed_by = processed_by
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


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
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='bns_comments',
                               related_query_name='bns_comment')
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='bns_%(class)ss',
                              related_query_name='bns_%(class)s')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.ForeignKey("Location", on_delete=models.PROTECT)
    image = models.ImageField(upload_to="items_image/", blank=True, null=True, default="items_image/default.png")
    views = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def get_content_type_id(self):
        return ContentType.objects.get_for_model(self).id


class Item(BaseOffer):
    is_active = models.BooleanField(default=True)

    comments = GenericRelation(
        "Comment",
        related_query_name="item_comment"
    )

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
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"

    def __str__(self):
        return f"{self.name} - {self.category}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bns_ratings',
    related_query_name='bns_rating')
    value = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинг"

    def __str__(self):
        obj_name = getattr(self.content_object, "name", str(self.content_object))
        return f"{obj_name} - рейтинг:{self.value}"


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bns_saved_items',
    related_query_name='bns_saved_item')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
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
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bns_sent_messages',
    related_query_name='bns_sent_message')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bns_received_messages',
    related_query_name='bns_received_message')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    room_name = models.CharField(max_length=255, default='')


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


class Complaint(models.Model):
    REASON_CHOICES = [
        ("swearing", "Образи / мова ненависті"),
        ('spam', 'Спам'),
        ('harassment', 'Переслідування'),
        ('inappropriate', 'Неприпустимий контент'),
        ('other', 'Інше'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bns_complaints")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="bns_complaints")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='swearing')
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Скарга"
        verbose_name_plural = "Скарги"

    def __str__(self):
        return f"Скарга від {self.author.username} на {self.content_object}"



class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking_user')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f'{self.blocker} blocked {self.blocked}'


class BlackList(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_others')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker} заблокував {self.blocked}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content}"


class ItemComplaint(models.Model):
    author = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_complaints")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="item_complaints_ct")
    object_id = models.PositiveIntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='owner_items_complaints')
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Скарга"
        verbose_name_plural = "Скарги"

    def clean(self):
        if self.owner == self.author:
            raise ValidationError("Користувач не може подати скаргу на свій товар.")

class UserComplaint(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_complaints")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Скарга на користувача"
        verbose_name_plural = "Скарги на користувачів"


    def clean(self):
        if self.author == self.user:
            raise ValidationError("Користувач не може подати скаргу сам на себе.")

    def __str__(self):
        return f"Скарга від {self.author.username} на {self.user.username}"
    

class OwnerAnalytics(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @property
    def total_views_services(self):
        services = Service.objects.filter(owner=self.owner)
        return sum(s.views for s in services)
    
    @property 
    def total_views_items(self):
        items = Item.objects.filter(owner=self.owner)
        return sum(i.views for i in items)
    

    @property 
    def average_product_rating(self):
        item = Item.objects.filter(owner = self.owner)
        rating = Rating.objects.filter(content_type = ContentType.objects.get_for_model(Item), object_id__in = [i.id for i in item])
        if rating.exists():
            return round(sum(r.value for r in rating)/ rating.count(), 1)
        return 0 
    
    @property 
    def total_item_complains(self):
        return ItemComplaint.objects.filter(owner=self.owner).count()
    
    @property 
    def total_user_complains(self):
        return UserComplaint.objects.filter(user=self.owner).count()
    
    @property
    def total_income(self):
        return self.owner.income


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує оплати'),
        ('paid', 'Оплачено'),
        ('processing', 'Обробляється'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(Item, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)

    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Замовлення #{self.id} від {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class SharedOrder(models.Model):
    STATUS_CHOICES = [
        ('collecting', 'Збір коштів'),
        ('paid', 'Оплачено'),
        ('processing', 'Обробляється'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shared_orders')
    items = models.ManyToManyField(Item, through='SharedOrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='collecting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    building = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    PAYMENT_CHOICES = [
        ('balance', 'З балансу'),
        ('card', 'Картка'),
        ('mixed', 'Змішана'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Спільне замовлення"
        verbose_name_plural = "Спільні замовлення"

    def __str__(self):
        return f"Спільне замовлення #{self.id} від {self.creator.username}"

    def is_fully_paid(self):
        return self.collected_amount >= self.total_amount

    def remaining_amount(self):
        return max(Decimal('0'), self.total_amount - self.collected_amount)

    def progress_percentage(self):
        if self.total_amount == 0:
            return 100
        return min(100, int((self.collected_amount / self.total_amount) * 100))


class SharedOrderItem(models.Model):
    shared_order = models.ForeignKey(SharedOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class SharedOrderContribution(models.Model):
    shared_order = models.ForeignKey(SharedOrder, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[
        ('balance', 'З балансу'),
        ('card', 'Картка'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shared_order', 'user')

    def __str__(self):
        return f"{self.user.username} внесок {self.amount} грн"

class DealHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    amount = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.product_name} — {self.total_price} грн"


class Map(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    city = models.ForeignKey(Location, max_length=100, on_delete=models.CASCADE)
    lat = models.FloatField(default=50.4501)
    lng = models.FloatField(default=30.5234)
    created_at = models.DateField(auto_now_add=True)

    @property
    def city_name(self):
        return self.city.city