from django import forms

from .models import Image, Property

#class FileFieldForm(forms.Form):
#    project_name = forms.CharField()
#    file_field = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class FileFieldForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ("image_dataset","image")

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
