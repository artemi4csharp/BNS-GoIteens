from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

User = settings.AUTH_USER_MODEL

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