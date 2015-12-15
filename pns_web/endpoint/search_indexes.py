from haystack import indexes
from endpoint.models import Mapping


class MappingIndex(indexes.SearchIndex, indexes.Indexable):
    username = indexes.CharField(model_attr='username')
    fullname = indexes.CharField(document=True)
