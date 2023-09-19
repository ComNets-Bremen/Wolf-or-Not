from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Subquery

from django.utils.html import mark_safe

import os
import uuid

class Class(models.Model):
    class_name          = models.CharField(max_length=100)
    class_id            = models.PositiveSmallIntegerField(unique=True)
    class_description   = models.TextField(blank=True)
    class_color         = models.CharField(max_length=12, default="00FF00")
    class_is_visible    = models.BooleanField(default=True)

    # Tries to automatically find the best color for the font
    def get_class_font_color(self):
        hex_color = self.class_color[1:]
        r, g, b =  tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        if round(((r*299)+(g*587)+(b*114))/1000) > 125:
            # black
            return "#000000"
        else:
            # white
            return "#FFFFFF"

    class Meta:
        ordering = ("class_id",)

    def __str__(self):
        return str(self.class_id) + ": " + self.class_name + (" 👁" if self.class_is_visible else "")

class Property(models.Model):
    property_name       = models.CharField(max_length=100)
    property_description= models.TextField(blank=True)

    def __str__(self):
        return self.property_name

class Dataset(models.Model):
    dataset_name        = models.CharField(max_length=100, unique=True)
    dataset_active      = models.BooleanField(default=True)
    dataset_max_polls   = models.PositiveSmallIntegerField(default=100)

    def get_number_images(self):
        return Image.objects.filter(image_dataset=self).count()
    get_number_images.short_description = "Number of images"

    def get_number_polls(self):
        return Poll.objects.filter(poll_image__image_dataset=self).count()
    get_number_polls.short_description = "Number of polls"

    def get_percentage_done(self):
        if self.dataset_max_polls > 0 and self.get_number_images() > 0:
            return round((self.get_number_polls() / (self.dataset_max_polls * self.get_number_images()))*100.0)
        return 0.0
    get_percentage_done.short_description = "Percentage done"

    def __str__(self):
        return self.dataset_name + " " + (u"✓" if self.dataset_active else u"✗")

class Image(models.Model):
    image           = models.ImageField(
            upload_to="images/%Y/%m/%d/",
            height_field="image_height",
            width_field="image_width")
    image_original_name = models.CharField(max_length=100, default="")
    image_uuid      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_width     = models.PositiveIntegerField(blank=True)
    image_height    = models.PositiveIntegerField(blank=True)
    image_dataset   = models.ForeignKey("Dataset", on_delete=models.CASCADE)

    def __str__(self):
        if len(self.image_original_name):
            return str(self.image_dataset) + ": " + self.image_original_name
        else:
            return str(self.image_dataset) + ": " + self.image.name

    def get_image_url(self):
        return reverse("get_image", kwargs={"uuid" : self.image_uuid})

    def get_original_image_url(self):
        return reverse("get_original_image", kwargs={"uuid" : self.image_uuid})

    def get_image_detail_url(self):
        return reverse("get_image_details", kwargs={"uuid" : self.image_uuid})

    def get_filename(self):
        return os.path.basename(self.image.name)

    def get_number_polls(self):
        return Poll.objects.filter(poll_image=self).count()

    def image_preview(self):
        return mark_safe('<img src = "{url}" width = "300"/>'.format(
             url = self.get_image_url()
         ))

    class Meta:
        ordering = ("image",)

class Poll(models.Model):
    poll_date = models.DateTimeField(auto_now_add=True, blank=True)
    poll_ip   = models.GenericIPAddressField(blank=True, null=True)
    poll_image= models.ForeignKey("Image", on_delete=models.CASCADE)
    poll_class= models.ManyToManyField("Class", blank=True)
    poll_property=models.ManyToManyField("Property", blank=True)

    def __str__(self):
        return "Poll on image " + str(self.poll_image)

# API Keys for direct data access

class ApiKey(models.Model):
    api_key_name  = models.CharField(max_length=100, unique=True)
    api_key       = models.UUIDField(primary_key=True, default=uuid.uuid4)
    api_key_level = models.IntegerField(default=0)

    def __str__(self):
        return str(self.api_key_name)


# Receiver functions

@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Image` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Image` object is updated
    with new file.
    """
    if len(instance.image_original_name) == 0:
        instance.image_original_name = instance.image.name


    if not instance.pk:
        return False

    try:
        old_file = Image.objects.get(pk=instance.pk).image
    except Image.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
