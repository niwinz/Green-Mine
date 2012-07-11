# -* coding: utf-8 -*-
from haystack import indexes
from .models import Project, Milestone, UserStory, Task


class ProjectIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/project_text.txt')

    def get_model(self):
        return Project

    def index_queryset(self):
        return self.get_model().objects.all()


class MilestoneIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/milestone_text.txt')

    def get_model(self):
        return Milestone

    def index_queryset(self):
        return self.get_model().objects.all()


class UserStoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/userstory_text.txt')

    def get_model(self):
        return UserStory

    def index_queryset(self):
        return self.get_model().objects.all()


class TaskIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/task_text.txt')

    def get_model(self):
        return Task

    def index_queryset(self):
        return self.get_model().objects.all()
