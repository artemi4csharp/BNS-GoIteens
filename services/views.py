from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Service
from .forms import ServiceCreationForm, ServiceEditForm

class ServiceListView(View):
    def get(self, request):
        service_type = request.GET.get("type")
        sort = request.GET.get('sort') or request.session.get('sort')
        
        if service_type in ["offer", "request"]:
            services = Service.objects.filter(service_type=service_type)
        else:
            services = Service.objects.all()
            
        if sort:
            request.session['sort'] = sort
            if sort == 'price_asc':
                services = services.order_by('price')
            elif sort == 'price_desc':
                services = services.order_by('-price')
            elif sort == 'name':
                services = services.order_by('name')
                
        last_seen_services = request.session.get("service_history", [])
        services_in_history = sorted(
            Service.objects.filter(pk__in=last_seen_services),
            key=lambda s: -last_seen_services.index(s.pk)
        )
        
        return render(request, "services/service_list.html", {
            "services": services,
            "services_in_history": services_in_history,
        })



class ServiceDetailView(View):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service_history = request.session.get('service_history', [])
        if pk not in service_history:
            service_history.append(pk)
            if len(service_history) > 5:
                service_history = service_history[-5:]
            request.session['service_history'] = service_history
            request.session.modified = True

        return render(request, "services/service_detail.html", {
            "service": service
        })


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
