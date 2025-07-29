from django import template

def add_class(field, css):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css})

register = template.Library()
register.filter('add_class', add_class)
