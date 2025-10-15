from django.core.cache import cache
from BNS_GoIteens.services.models import Category, Item, Service


def get_top_categories():
    key = "top_categories"
    data = cache.get(key)
    if not data:
        data = list(Category.objects.filter(is_active=True).order_by("-views")[:5])
        cache.set(key, data, 60 * 10)
    return data


def get_filtered_services(service_type=None):
    key = f"filtered_services_{service_type or 'all'}"
    data = cache.get(key)
    if not data:
        if service_type in ["offer", "request"]:
            data = list(Service.objects.filter(service_type=service_type))
        else:
            data = list(Service.objects.all())
        cache.set(key, data, 30)
    return data


def get_all_categories():
    key = "all_categories"
    data = cache.get(key)
    if not data:
        data = list(Category.objects.filter(is_active=True))
        cache.set(key, data, 60 * 60)  # 1 час
    return data


def get_popular_items():
    key = "popular_items"
    data = cache.get(key)
    if not data:
        data = list(Item.objects.order_by("-views")[:10])
        cache.set(key, data, 60 * 5)
    return data


def get_analytics_data():
    key = "analytics_data"
    data = cache.get(key)
    if not data:
        total_items = Item.objects.count()
        total_services = Service.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        data = {
            "total_items": total_items,
            "total_services": total_services,
            "active_categories": active_categories,
        }
        cache.set(key, data, 60 * 15)
    return data


def clear_cache_for_model(model_name):
    keys_to_clear = []
    if model_name == "Category":
        keys_to_clear = ["top_categories", "all_categories", "analytics_data"]
    elif model_name == "Item":
        keys_to_clear = ["popular_items", "analytics_data"]
    elif model_name == "Service":
        keys_to_clear = ["filtered_services_offer", "filtered_services_request", "analytics_data"]

    for key in keys_to_clear:
        cache.delete(key)
