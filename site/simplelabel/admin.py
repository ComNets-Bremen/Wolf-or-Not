from django.contrib import admin

from .models import Class, Property, Dataset, Image, Poll, ApiKey

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    readonly_fields = ("get_class_font_color",)
    pass

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("image", "image_height", "image_width", "image_uuid", "get_image_url", "get_number_polls", "image_original_name", "image_preview")
    list_filter = ("image_dataset",)
    list_display = ("__str__", "get_number_polls",)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('dataset_name', 'dataset_active', 'get_number_images', 'dataset_max_polls', 'get_number_polls', 'get_percentage_done')
    readonly_fields = ('get_number_images', 'get_number_polls', 'get_percentage_done')


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    readonly_fields = ("poll_date",)
    list_filter = ('poll_image__image_dataset',)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    pass
