# -* coding: utf-8 -*-
from haystack import indexes
from .models import WikiPage, WikiPageAttachment,  WikiPageHistory


class WikiPageIndex(indexes.RealTimeSearchIndex, indexes.Indexable):i
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return WikiPage

    def index_queryset(self):
        return self.get_model().objects.all()


class WikiPageAttachmentIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    wikipage = indexes.CharField(model_attr='wikipage')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return WikiPageHistory

    def index_queryset(self):
        return self.get_model().objects.all()


class WikiPageHistoryIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    wikipage = indexes.CharField(model_attr='wikipage')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return WikiPageHistory

    def index_queryset(self):
        return self.get_model().objects.all()
