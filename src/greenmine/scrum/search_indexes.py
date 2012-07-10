# -* coding: utf-8 -*-
from haystack import indexes
from .models import Project, Milestone, UserStory, Task


class ProjectIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    created_date = indexes.DateTimeField(model_attr='created_date')
    extras = indexes.CharField(model_attr='extras', null=True)

    def get_model(self):
        return Project

    def index_queryset(self):
        return self.get_model().objects.all()


class MilestoneIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return Milestone

    def index_queryset(self):
        return self.get_model().objects.all()


class UserStoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner', null=True)
    project = indexes.CharField(model_attr='project')
    milestone = indexes.CharField(model_attr='milestone', null=True)
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return UserStory

    def index_queryset(self):
        return self.get_model().objects.all()


class TaskIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    owner = indexes.CharField(model_attr='owner')
    project = indexes.CharField(model_attr='project')
    milestone = indexes.CharField(model_attr='milestone', null=True)
    user_story = indexes.CharField(model_attr='user_story', null=True)
    created_date = indexes.DateTimeField(model_attr='created_date')

    def get_model(self):
        return Task

    def index_queryset(self):
        return self.get_model().objects.all()
