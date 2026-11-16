from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class Patent(models.Model):
    doc_number = models.CharField(max_length=64, primary_key=True)
    title = models.TextField(null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    classification = models.TextField(null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)
    filename = models.TextField(null=True, blank=True)
    source_file = models.TextField()
    record_index = models.PositiveIntegerField()
    content_sha256 = models.CharField(max_length=64)
    raw_record = models.JSONField()
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        ordering = ["doc_number"]
        indexes = [GinIndex(fields=["search_vector"], name="patent_search_vector_gin")]
