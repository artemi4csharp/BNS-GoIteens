from django.db import models
from django.conf import settings
from django.utils import timezone


class SupportSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('active', 'Активний'),
        ('closed', 'Закритий'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_sessions')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_sessions')
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Сесія підтримки"
        verbose_name_plural = "Сесії підтримки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Підтримка #{self.id} - {self.user.username} ({self.status})"


class SupportMessage(models.Model):
    session = models.ForeignKey(SupportSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_agent_message = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Повідомлення підтримки"
        verbose_name_plural = "Повідомлення підтримки"
        ordering = ['created_at']

    def __str__(self):
        return f"Повідомлення від {self.sender.username} у сесії #{self.session.id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_agent_message = self.sender.is_staff
        super().save(*args, **kwargs)
