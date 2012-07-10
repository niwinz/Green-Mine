# -* coding: utf-8 -*-
from django.contrib.auth.models import User
from haystack import indexes
from .models import Profile

class UserIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)

    def get_model(self):
        return User

    def index_queryset(self):
        return self.get_model().objects.all()


class ProfileIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='user')

    def get_model(self):
        return Profile

    def index_queryset(self):
        return self.get_model().objects.all()
