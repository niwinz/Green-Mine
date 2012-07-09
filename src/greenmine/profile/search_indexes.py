# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    pass
