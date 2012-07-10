# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class DocumentIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return Document

    def index_queryset(self):
        return self.get_model().objects.all()
