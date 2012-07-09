from django.db import models

class WikiField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        from greenmine.wiki.forms import WikiFormField
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': WikiFormField}
        defaults.update(kwargs)
        return super(WikiField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.TextField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
