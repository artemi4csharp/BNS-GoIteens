from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Service
from .forms import ServiceCreationForm, ServiceEditForm

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
