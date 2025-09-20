from django.contrib import admin
from .models import Category, CategoryRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_by', 'created_at')
    search_fields = ('name',)


@admin.register(CategoryRequest)
class CategoryRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'created_at', 'processed_at', 'processed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'user__username')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for req in queryset.filter(status=CategoryRequest.STATUS_PENDING):
            req.approve(processed_by=request.user)
        self.message_user(request, "Вибрані запити підтверджено і категорії створено.")
    approve_requests.short_description = "Підтвердити вибрані запити"

    def reject_requests(self, request, queryset):
        for req in queryset.filter(status=CategoryRequest.STATUS_PENDING):
            req.reject(processed_by=request.user)
        self.message_user(request, "Вибрані запити відхилено.")
    reject_requests.short_description = "Відхилити вибрані запити"
