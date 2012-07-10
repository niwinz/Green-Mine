# -* coding: utf-8 -*-
from haystack import indexes
from .models import Question, QuestionResponse


class QuestionIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    milestone = indexes.CharField(model_attr='milestone', null=True)
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return Question

    def index_queryset(self):
        return self.get_model().objects.all()


class QuestionResponseIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    question  = indexes.CharField(model_attr='question')
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return QuestionResponse

    def index_queryset(self):
        return self.get_model().objects.all()
