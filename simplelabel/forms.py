from django import forms
from django.templatetags.static import static
from django.db.models import Count


from .models import Image, Property, Dataset

#class FileFieldForm(forms.Form):
#    project_name = forms.CharField()
#    file_field = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class FileFieldForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ("image_dataset","image")

    class Media:
        js = (static('js/upload_form.js'),)

    def __init__(self, *args, **kwargs):
        super(FileFieldForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget.attrs["multiple"] = True

class PollForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        props = Property.objects.all().values_list("id", "property_name")

        self.fields["properties"] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple,
            choices=props,
            )

class DownloadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dataset_ids = Image.objects.all().values("image_dataset").distinct()
        choices = Dataset.objects.filter(id__in=dataset_ids).values_list("id", "dataset_name")

        p = Image.objects.all().annotate(num_polls=Count("poll", distinct=True)).order_by("-num_polls").values_list("num_polls").distinct()
        num_polls = [(i, "At least "+str(i) + " polls") for i in range(max(p)[0]+1)]


        self.fields["datasets"] = forms.MultipleChoiceField(
                label="Use these datasets",
                required=True,
                widget=forms.CheckboxSelectMultiple,
                choices=choices,
                )

        self.fields["num_polls"] = forms.CharField(
                label="Min number of polls",
                required = True,
                widget=forms.Select(choices=num_polls),
                )
