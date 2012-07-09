from django.forms.fields import CharField as DjangoCharField
from greenmine.wiki.widgets import WikiWidget
from django import forms
from greenmine.wiki.models import WikiPage

class WikiFormField(DjangoCharField):
    def __init__(self, *args, **kwargs):
        self.widget = WikiWidget
        super(WikiFormField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(WikiFormField, self).widget_attrs(widget)
        if "class" not in attrs:
            attrs['class'] = ''
        current_clases = attrs['class'].split()
        current_clases.append('wiki_field')
        attrs['class'] = ' '.join(current_clases)
        return attrs


class WikiPageEditForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = ('content',)
