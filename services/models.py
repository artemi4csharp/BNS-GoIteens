from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(verbose_name="Активно")
    views = models.PositiveIntegerField(default=0)

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

    def __str__(self):
        return f"{self.country}:{self.region or 'Немає'}:{self.city}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_comments',
    related_query_name='services_comment')
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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_%(class)ss',
    related_query_name='services_%(class)s')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.ForeignKey("Location", on_delete=models.PROTECT)
    image = models.ImageField(upload_to="items_image/", blank=True, null=True)

    class Meta:
        abstract = True


class Item(BaseOffer):

    def average_rating(self):
        return round(self.ratings.aggregate(avg=models.Avg("value"))["avg"] or 0, 1)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return f'{self.name} - {self.category}'


class Service(BaseOffer):
    service_type = models.CharField(choices=[("offer", "Надаю"), ("request", "Шукаю")])

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"

    def __str__(self):
        return f"{self.name} - {self.category}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_ratings',
    related_query_name='services_rating')
    value = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="ratings")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        verbose_name = "Рейтинг"

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_saved_items',
    related_query_name='services_saved_item')
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
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_sent_messages',
    related_query_name='services_sent_message')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services_received_messages',
    related_query_name='services_received_message')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Написав {self.sender} до {self.receiver}"


class BlackList(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocked_users")
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="in_blacklist")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")
        verbose_name = "Чорний список"
        verbose_name_plural = "Чорний список"

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


class Complaint(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Скарга"
        verbose_name_plural = "Скарги"

    def __str__(self):
        return f"Скарга від {self.author.username} на {self.content_object}"