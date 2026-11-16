from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Patent",
            fields=[
                ("doc_number", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("title", models.TextField(blank=True, null=True)),
                ("abstract", models.TextField(blank=True, null=True)),
                ("classification", models.TextField(blank=True, null=True)),
                ("bibtex", models.TextField(blank=True, null=True)),
                ("filename", models.TextField(blank=True, null=True)),
                ("source_file", models.TextField()),
                ("record_index", models.PositiveIntegerField()),
                ("content_sha256", models.CharField(max_length=64)),
                ("raw_record", models.JSONField()),
            ],
            options={"ordering": ["doc_number"]},
        ),
        migrations.CreateModel(
            name="Passage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_field", models.CharField(
                    choices=[("claims", "Claims"), ("detailed_description", "Description")],
                    max_length=32,
                )),
                ("source_index", models.PositiveIntegerField()),
                ("text", models.TextField()),
                ("patent", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="passages",
                    to="patents.patent",
                )),
            ],
            options={
                "ordering": ["patent_id", "source_field", "source_index"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("patent", "source_field", "source_index"),
                        name="unique_source_passage",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(source_field__in=["claims", "detailed_description"]),
                        name="valid_passage_source_field",
                    ),
                ],
            },
        ),
    ]
