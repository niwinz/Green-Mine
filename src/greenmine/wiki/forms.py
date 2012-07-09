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
