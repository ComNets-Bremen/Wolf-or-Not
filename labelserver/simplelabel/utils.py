import re

from django.db import models
from django import forms


class HexFormField(forms.CharField):
    default_error_messages = {
        'invalid': 'Enter a valid hexfigure: e.g. "ff0022"',
    }

    def clean(self, value):
        print("here", value)
        if (not (value == '' and not self.required) and
                not re.match('^[A-Fa-f0-9]+$', value)):
            raise forms.ValidationError(self.error_messages['invalid'])
        return value


class HexField(models.BigIntegerField):
    """
    Field to store hex values.

    On Database side an integerfield is used.
    """
    # TODO: Use same sort of BigPositiveIntegerField
    description = "Saves a hex value into an IntegerField"

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            hex_value = value
        else:
            hex_value = hex(value)[2:]
            hex_value = (8 - len(hex_value)) * '0' + hex_value
        return hex_value

    def get_prep_value(self, value):
        return int(value, 16)

    def formfield(self, **kwargs):
        #kwargs['form_class'] = HexFormField
        # Use the Field base method without super to skip the validation of the
        # PositiveInterField
        #return models.fields.Field.formfield(self, **kwargs)

        defaults = {'form_class': HexFormField}
        defaults.update(kwargs)
        #return super().formfield(**defaults)
        return models.fields.Field.formfield(self, **defaults)
