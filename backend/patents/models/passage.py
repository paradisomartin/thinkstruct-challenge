from django.db import models


class Passage(models.Model):
    class SourceField(models.TextChoices):
        CLAIMS = "claims"
        DESCRIPTION = "detailed_description"

    patent = models.ForeignKey("patents.Patent", on_delete=models.CASCADE, related_name="passages")
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
