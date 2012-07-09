# -*- coding: utf-8 -*-

from django.template.defaultfilters import slugify

def slugify_uniquely(value, model, slugfield="slug"):
    """
    Returns a slug on a name which is unique within a model's table
    self.slug = SlugifyUniquely(self.name, self.__class__)
    """
    suffix = 0
    potential = base = slugify(value)
    if len(potential) == 0:
        potential = 'null'
    while True:
        if suffix:
            potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
            return potential
        suffix += 1
