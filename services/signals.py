from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Item, Service
from BNS_GoIteens.django_cache.cache_utils import clear_cache_for_model


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    clear_cache_for_model("Category")


@receiver([post_save, post_delete], sender=Item)
def clear_item_cache(sender, **kwargs):
    clear_cache_for_model("Item")


@receiver([post_save, post_delete], sender=Service)
def clear_service_cache(sender, **kwargs):
    clear_cache_for_model("Service")
