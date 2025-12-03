from django import template
import base64

def add_class(field, css):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css})

def base64encode(value):
    if value:
        return base64.b64encode(value).decode('utf-8')
    return ''

register = template.Library()
register.filter('add_class', add_class)
register.filter('base64encode', base64encode)
