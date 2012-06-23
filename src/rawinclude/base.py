# -*- coding: utf-8 -*-

from django.template.loader import find_template_loader, TemplateDoesNotExist
from django.conf import settings

template_cache = {}
template_source_loaders = None


def find_template(name, dirs=None):
    global template_source_loaders

    if template_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)

    for loader in template_source_loaders:
        try:
            return loader.load_template_source(name)
        except TemplateDoesNotExist:
            continue

    raise TemplateDoesNotExist(name)
