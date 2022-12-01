from django.contrib import admin

from .models import Class, Property, Dataset, Image, Poll, ApiKey

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    pass

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("image_height", "image_width", "image_uuid", "get_image_url")
    list_filter = ("image_dataset",)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    readonly_fields = ("poll_date",)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    pass
