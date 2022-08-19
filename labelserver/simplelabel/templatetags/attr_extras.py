from django import template

register = template.Library()

def htmlattributes(value, arg):
    attrs = value.field.widget.attrs
    data = arg.replace(' ', '')

    kvs = data.split(',')

    for string in kvs:
        kv = string.split(':')
        attrs[kv[0]] = kv[1]

    rendered = str(value)

    return rendered

register.filter('htmlattributes', htmlattributes)
