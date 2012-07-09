# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class DocumentIndex(indexes.SearchIndex, indexes.Indexable):
    pass
