# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    pass


class QuestionResponseIndex(indexes.SearchIndex, indexes.Indexable):
    pass
