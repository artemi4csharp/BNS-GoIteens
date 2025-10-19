from django.shortcuts import render, redirect
import requests 
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from bns_goiteens.models import Map, Item
import json 
from django.shortcuts import get_object_or_404

def items_location(request):
    items_locations = Item.objects.filter(owner=request.user)
    points = Map.objects.filter(user=request.user).values("lat", "lng", "city__city")
    points_json = json.dumps(list(points), ensure_ascii=False)
    return render(request, 'item_location.html', {
        "location": items_locations,
        "points_json": points_json
    })

@login_required
def add_map_point(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if not item_id:
            return JsonResponse({'status': 'error', 'error': 'Оберіть товар!'})

        try:
            item = Item.objects.get(id=item_id, owner=request.user)
            city = item.location
            city_name = city.city

            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": city_name, 'format': 'json', 'limit': 1}
            r = requests.get(url, params=params, headers={'User-Agent': 'bns-goiteens'})
            coords = r.json()
            if not coords:
                return JsonResponse({'status': 'error', 'error': f'Місто {city_name} не знайдено'})

            lat = float(coords[0]['lat'])
            lng = float(coords[0]['lon'])

            Map.objects.create(user=request.user, city=city, lat=lat, lng=lng)

            return JsonResponse({'status': 'ok', 'lat': lat, 'lng': lng, 'city': city_name})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    else:
        return JsonResponse({'status': 'error', 'error': 'Не дозволений метод'})
