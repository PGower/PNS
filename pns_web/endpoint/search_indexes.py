from haystack import indexes
from endpoint.models import Fullname


class FullnameIndex(indexes.SearchIndex, indexes.Indexable):
    username = indexes.CharField(model_attr='username')
    fullname = indexes.CharField(model_attr='fullname')
    text = indexes.EdgeNgramField(model_attr='fullname', document=True)

    def get_model(self):
        return Fullname

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
