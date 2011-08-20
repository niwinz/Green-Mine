# Copied from http://www.djangosnippets.org/snippets/1669/
#
# We would like to use a BlobField but that doesn't exist in Django yet:
# http://code.djangoproject.com/ticket/2417

import base64

from django.db import models


class Base64Field(models.TextField):

    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.b64decode(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.b64encode(data))
