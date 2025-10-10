from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Service, Item, Comparison
from .forms import ServiceCreationForm, ServiceEditForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET

class ServiceListView(View):
    def get(self, request):
        service_type = request.GET.get("type")
        if service_type in ["offer", "request"]:
            services = Service.objects.filter(service_type=service_type)
        else:
            services = Service.objects.all()
        return render(request, "services/service_list.html", {"services": services})



class ServiceDetailView(View):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        return render(request, "services/service_detail.html", {"service": service})


class ServiceCreateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        form = ServiceCreationForm()
        return render(request, "services/service_form.html", {"form": form})

    def post(self, request):
        form = ServiceCreationForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.owner = request.user
            service.save()
            return redirect("service_list")
        return render(request, "services/service_form.html", {"form": form})


class ServiceUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        if service.owner != request.user:
            return redirect("service_list")
        form = ServiceEditForm(queryset=Service.objects.filter(pk=pk))
        return render(request, "services/service_form.html", {"form": form})

    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        if service.owner != request.user:
            return redirect("service_list")
        form = ServiceEditForm(request.POST, queryset=Service.objects.filter(pk=pk))
        if form.is_valid():
            form.save()
            return redirect("service_list")
        return render(request, "services/service_form.html", {"form": form})


class ServiceDeleteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        if service.owner != request.user:
            return redirect("service_list")
        return render(request, "services/service_confirm_delete.html", {"service": service})

    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        if service.owner != request.user:
            return redirect("service_list")
        service.delete()
        return redirect("service_list")

@require_POST
def add_to_comparison(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.user.is_authenticated:
        comparison, created = Comparison.objects.get_or_create(user=request.user)
        comparison.items.add(item)
    else:
        compare_list = request.session.get('compare_list', [])
        if item_id not in compare_list:
            compare_list.append(item_id)
        request.session['compare_list'] = compare_list

    return JsonResponse({'success': True, 'message': f'{item.name} додано до порівняння'})


@require_http_methods(["DELETE"])
def remove_from_comparison(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.user.is_authenticated:
        try:
            comparison = Comparison.objects.get(user=request.user)
            comparison.items.remove(item)
        except Comparison.DoesNotExist:
            pass
    else:
        compare_list = request.session.get('compare_list', [])
        if item_id in compare_list:
            compare_list.remove(item_id)
            request.session['compare_list'] = compare_list

    return JsonResponse({'success': True, 'message': f'{item.name} видалено з порівняння'})


@require_GET
def get_comparison(request):
    if request.user.is_authenticated:
        comparison, _ = Comparison.objects.get_or_create(user=request.user)
        items = comparison.items.all()
    else:
        compare_list = request.session.get('compare_list', [])
        items = Item.objects.filter(id__in=compare_list)

    data = [
        {
            'id': item.id,
            'name': item.name,
            'category': item.category.name,
            'price': float(item.price),
            'rating': item.average_rating(),
        }
        for item in items
    ]

    return JsonResponse({'items': data})
