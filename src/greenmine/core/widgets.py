from django.forms import widgets

class WikiWidget(widgets.Textarea):
    attr = {'class': 'wiki_field'}
