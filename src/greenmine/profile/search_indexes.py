# -* coding: utf-8 -*-
from django.contrib.auth.models import User
from haystack import indexes

class UserIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/user_text.txt')

    def get_model(self):
        return User

    def index_queryset(self):
        return self.get_model().objects.all()
