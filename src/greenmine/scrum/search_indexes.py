# -* coding: utf-8 -*-
from haystack import indexes
from .models import Document


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    pass


class MilestoneIndex(indexes.SearchIndex, indexes.Indexable):
    pass


class UserStoryIndex(indexes.SearchIndex, indexes.Indexable):
    pass


class TaskIndex(indexes.SearchIndex, indexes.Indexable):
    pass
