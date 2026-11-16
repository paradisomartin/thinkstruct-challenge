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


class Passage(models.Model):
    class SourceField(models.TextChoices):
        CLAIMS = "claims"
        DESCRIPTION = "detailed_description"

    patent = models.ForeignKey(Patent, on_delete=models.CASCADE, related_name="passages")
    source_field = models.CharField(max_length=32, choices=SourceField.choices)
    source_index = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        ordering = ["patent_id", "source_field", "source_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["patent", "source_field", "source_index"],
                name="unique_source_passage",
            ),
            models.CheckConstraint(
                condition=models.Q(source_field__in=["claims", "detailed_description"]),
                name="valid_passage_source_field",
            ),
        ]
