from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse, Http404
from django.urls import reverse

from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Count

from collections import Counter

import random
from uuid import UUID

from PIL import Image as PI
from PIL import ImageOps as PIO

from io import BytesIO

from .forms import FileFieldForm, PollForm, DownloadForm

from .models import Image, Dataset, Class, Property, Poll, ApiKey

import numpy as np

import datetime


MAX_STANDARD_IMG_SIZE = 400

def index(request):
    return render(request, 'simplelabel/index.html')

## Redirect app from / to here
def redirect_to_here(request):
    return HttpResponseRedirect(reverse("index"))


"""
Show some simple statistics of the data currently being labeled
"""
def get_statistics(request):
    p = Image.objects.filter(image_dataset__dataset_active=True).annotate(num_polls=Count("poll", distinct=True)).order_by("-num_polls").values_list("num_polls", "image_uuid")

    values = [i[0] for i in p]

    frequencies = Counter(values).most_common()
    frequencies.sort(key = lambda x : x[1], reverse=False)
    freq_list_dict = []

    sufficient_polls_3 = 0

    for f in frequencies:
        # count number of images with at least 3 polls
        if f[0] >= 3:
            sufficient_polls_3 += f[1]
        freq_list_dict.append({
                "number_polls" : f[0],
                "number_images" : f[1],
                "percentage_images" : round(f[1] / len(p) * 100.0, 2),
                })

    freq_list_dict = sorted(freq_list_dict, key=lambda d: d["number_polls"])

    data = {
            "image_count" : Image.objects.filter(image_dataset__dataset_active=True).count(),
            "poll_count" : Poll.objects.filter(poll_image__image_dataset__dataset_active=True).count(),
            "mean_count_image" : round(np.mean(values),2) if len(values) else 0,
            "max_count_image" : np.max(values) if len(values) else 0,
            "min_count_image" : np.min(values) if len(values) else 0,
            "median_count_image" : np.median(values) if len(values) else 0,
            "frequencies" : frequencies,
            "freq_list_dict" : freq_list_dict,
            "percent_done_3" : round(sufficient_polls_3/len(p)*100,2) if len(p) else 0,
            }


    return render(request, 'simplelabel/statistics.html', data)


"""
Show the requested image and make sure it is something which can be shown in the Webbrowser
"""
def get_image(request, uuid, max_size=MAX_STANDARD_IMG_SIZE, only_downscale=False):
    image = get_object_or_404(Image, image_uuid=uuid).image

    authenticated = request.user.is_authenticated

    if not authenticated and "HTTP_AUTHORIZATION" in request.META:
        auth_header = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth_header) == 2 and auth_header[0] == "Token":
            key = auth_header[1]
            print("Checking key:", key)
            try:
                key = UUID(key, version=4)
            except ValueError:
                print("Not a valid token")
                key = None
                return HttpResponse("Invalid token", status="402")

            if key and ApiKey.objects.filter(api_key=key).count():
                print("Valid token")
                authenticated = True
        else:
            print("Not a valid header:", auth_header)
            return HttpResponse("Invalid Auth header", status=402)

    if not authenticated and (max_size is None or max_size > MAX_STANDARD_IMG_SIZE):
        max_size=MAX_STANDARD_IMG_SIZE

    im = PI.open(image)
    si = im.convert("RGB")
    if max_size:
        if only_downscale:
            si.thumbnail((max_size, max_size))
        else:
            si = PIO.contain(si, (max_size, max_size))
    out = BytesIO()
    si.save(out, format="JPEG")
    im.close()
    out.seek(0)

    return FileResponse(out, content_type="image/jpeg")

"""
View to upload additional images
"""
class UploadImagesView(LoginRequiredMixin, CreateView):
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

        #return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


"""
The poll view: Get a random image, show it and store the poll results to the
database.
"""
class PollImageView(FormView):
    form_class = PollForm
    template_name = "simplelabel/poll.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pks = Image.objects.filter(image_dataset__dataset_active=True).values_list('pk', flat=True)
        if len(pks) == 0:
            raise Http404("No polls available yet. Please return later")
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

"""
Download the wolf images

TODO: A lot of optimization...
"""
class DownloadView(LoginRequiredMixin, FormView):
    form_class = DownloadForm
    template_name = "simplelabel/download.html"

    def get_success_url(self):
        return reverse('download_results')

    def form_valid(self, form):
        datasets = get_list_or_404(Dataset, id__in=form.cleaned_data["datasets"])
        min_num_polls = form.cleaned_data["num_polls"]

        related_images = Image.objects.all().annotate(num_polls=Count("poll", distinct=True)).filter(num_polls__gte=min_num_polls, image_dataset__in=datasets)
        related_polls = Poll.objects.filter(poll_image__in=related_images)

        classes = { cls[0]: (cls[1], cls[2]) for cls in Class.objects.all().values_list('id', 'class_name', 'class_id')}
        properties = { prop[0]: prop[1] for prop in Property.objects.all().values_list('id', 'property_name')}

        server = self.request.get_host()

        ret = {}
        ret["export_datetime"] = datetime.datetime.now()
        ret["export_server"] = server
        ret["images"] = []
        ret["classes"] = [{"class_name" : cls[0], "class_id" : cls[1]} for cls in Class.objects.all().values_list('class_name', 'class_id')]
        ret["properties"] = [p[0] for p in Property.objects.all().values_list('property_name')]

        for image in related_images:
            img = {}
            img["image_name"]    = image.get_filename()
            img["image_uuid"]    = image.image_uuid
            img["image_url"]     = server + image.get_image_url()
            img["image_dataset"] = image.image_dataset.dataset_name
            img["polls"] = []
            num_class_ids = []
            for poll in Poll.objects.filter(poll_image=image).prefetch_related('poll_class', 'poll_property'):
                d = {}
                cls = poll.poll_class.all()[0]
                d["class"] = cls.class_name
                d["class_id"] = cls.class_id
                num_class_ids.append(cls.class_id)
                d["properties"] = [p.property_name for p in poll.poll_property.all()]
                img["polls"].append(d)

            class_id_counts = {ids:num_class_ids.count(ids)/len(num_class_ids) for ids in num_class_ids}
            img["relative_class_voting"] = class_id_counts

            ret["images"].append(img)

        response = JsonResponse(ret)
        response['Content-Disposition'] = 'attachment; filename=export.json'
        return response

