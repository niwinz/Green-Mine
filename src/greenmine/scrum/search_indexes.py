# -* coding: utf-8 -*-
from haystack import indexes
from .models import Project, Milestone, UserStory, Task


class ProjectIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    created_date = indexes.DateTimeField(model_attr='created_data')
    extra = indexes.DateTimeField(model_attr='extra')

    def get_model(self):
        return Project

    def index_queryset(self):
        return self.get_model().objects.all()


class MilestoneIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return Milestone

    def index_queryset(self):
        return self.get_model().objects.all()


class UserStoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    milestone = indexes.CharField(model_attr='milestone')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return UserStory

    def index_queryset(self):
        return self.get_model().objects.all()


class TaskIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    milestone = indexes.CharField(model_attr='milestone')
    user_story = indexes.CharField(model_attr='user_story')
    created_date = indexes.DateTimeField(model_attr='created_data')

    def get_model(self):
        return Task

    def index_queryset(self):
        return self.get_model().objects.all()
