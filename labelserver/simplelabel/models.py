from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.urls import reverse
import os
import uuid

class Class(models.Model):
    class_name          = models.CharField(max_length=100)
    class_id            = models.PositiveSmallIntegerField(unique=True)
    class_description   = models.TextField(blank=True)
    class_color         = models.CharField(max_length=12, default="00FF00")

    class Meta:
        ordering = ("class_id",)

    def __str__(self):
        return str(self.class_id) + ": " + self.class_name

class Property(models.Model):
    property_name       = models.CharField(max_length=100)
    property_description= models.TextField(blank=True)

    def __str__(self):
        return self.property_name

class Dataset(models.Model):
    dataset_name        = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.dataset_name

class Image(models.Model):
    image = models.ImageField(
            upload_to="images/%Y/%m/%d/",
            height_field="image_height",
            width_field="image_width")
    image_uuid      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_width     = models.PositiveIntegerField(blank=True)
    image_height    = models.PositiveIntegerField(blank=True)
    image_dataset   = models.ForeignKey("Dataset", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.image_dataset) + ": " + self.image.name

    def get_image_url(self):
        return reverse("get_image", kwargs={"uuid" : self.image_uuid})


class Poll(models.Model):
    poll_date = models.DateTimeField(auto_now_add=True, blank=True)
    poll_ip   = models.GenericIPAddressField(blank=True, null=True)
    poll_image= models.ForeignKey("Image", on_delete=models.CASCADE)
    poll_class= models.ManyToManyField("Class", blank=True)
    poll_property=models.ManyToManyField("Property", blank=True)

    def __str__(self):
        return "Poll on image " + str(self.poll_image)


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
