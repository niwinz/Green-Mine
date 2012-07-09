# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class WikiPageIndex(indexes.SearchIndex, indexes.Indexable):
    pass


class WikiPageHistoryIndex(indexes.SearchIndex, indexes.Indexable):
    pass
