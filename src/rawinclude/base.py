# -*- coding: utf-8 -*-

from django.template import loader

template_cache = {}

def find_template(path):
   source, origin = loader.find_template(path)
   return source, origin
