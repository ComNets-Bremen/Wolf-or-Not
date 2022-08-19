from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.urls import reverse

from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import random
from uuid import UUID

from PIL import Image as PI
from io import BytesIO

from .forms import FileFieldForm, PollForm

from .models import Image, Dataset, Class, Poll


def index(request):
    return render(request, 'simplelabel/index.html')

## Redirect app from / to here
def redirect_to_here(request):
    return HttpResponseRedirect(reverse("index"))


def get_image(request, uuid, max_size=400):
    image = get_object_or_404(Image, image_uuid=uuid).image
    im = PI.open(image)
    si = im.convert("RGB")
    si.thumbnail((max_size, max_size))
    out = BytesIO()
    si.save(out, format="JPEG")
    out.seek(0)

    return FileResponse(out)

class UploadImagesView(LoginRequiredMixin, FormView):
    form_class = FileFieldForm
    template_name = "simplelabel/upload.html"
    def get_success_url(self):
        return reverse('upload_images')

    def form_valid(self, form):
        image_dataset = form.cleaned_data["image_dataset"]
        for i in form.files.getlist("image"):
            print("Adding image", i)
            print(type(i), i.size)
            Image.objects.create(image=i, image_dataset=image_dataset).save()

        return super().form_valid(form)


class PollImageView(FormView):
    form_class = PollForm
    template_name = "simplelabel/poll.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pks = Image.objects.values_list('pk', flat=True)
        random_pk = random.choice(pks)
        random_img = Image.objects.get(pk=random_pk)

        classes = Class.objects.all()
        context["classes"] = classes
        context["image"] = random_img
        return context

    def get_success_url(self):
        return reverse('poll')

    def form_valid(self, form):
        button = list(filter(lambda c : c.startswith("submit_"), self.request.POST.keys()))
        if len(button) != 1:
            return HttpResponse("Invalid Button", status=500)
        class_id = int(button[0].split("_")[-1])
        cls = get_object_or_404(Class, class_id=class_id)


        image_uuid = UUID(self.request.POST["image_uuid"])
        image = Image.objects.get(image_uuid=image_uuid)
        print(image)

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        print("IP", ip, "class", cls)

        props = form.cleaned_data["properties"]

        p = Poll.objects.create(poll_ip=ip, poll_image=image)
        p.poll_class.set((cls,))
        p.poll_property.set(props)
        p.save()
        return super().form_valid(form)

