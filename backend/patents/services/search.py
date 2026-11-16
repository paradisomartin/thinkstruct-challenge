"""Patent-level lexical retrieval; literal metadata constraints are separate."""

import re

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db.models import Case, F, IntegerField, Value, When

from patents.models import Passage, Patent


class SearchInputError(ValueError):
    pass


def tokens(text):
    return re.findall(r"[^\W_]+", text.casefold())


def normalized_title(text):
    return " ".join(text.casefold().split())


def _text(value, name):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise SearchInputError(f"{name} must be text")
    return value.strip()


def _keywords(value, name):
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise SearchInputError(f"{name} must be a list of single-token terms")
    terms = []
    for item in value:
        item = _text(item, name)
        parts = tokens(item)
        if len(parts) != 1:
            raise SearchInputError(f"Each {name} term must normalize to one token")
        if parts[0] not in terms:
            terms.append(parts[0])
    return terms


def _excerpts(page, evidence_query, effective):
    """Any query lexeme can explain a cross-field match, not necessarily all."""
    excerpts = {}
    ids = [patent.pk for patent in page]
    if not ids:
        return excerpts
    if evidence_query is not None:
        passages = (
            Passage.objects.filter(patent_id__in=ids)
            .annotate(vector=SearchVector("text", config="english"))
            .filter(vector=evidence_query)
            .annotate(
                # A string makes SearchRank re-tokenize vector::text.
                rank=SearchRank(F("vector"), evidence_query),
                preference=Case(
                    When(source_field="claims", then=Value(0)),
                    default=Value(1), output_field=IntegerField(),
                ),
            )
            .order_by("patent_id", "preference", "-rank", "source_index")
            .distinct("patent_id")
        )
        for passage in passages:
            excerpts.setdefault(passage.patent_id, {
                "text": passage.text,
                "source_field": passage.source_field,
                "source_index": passage.source_index,
            })
        for field in ("title", "abstract"):
            matches = (
                Patent.objects.filter(pk__in=ids)
                .annotate(vector=SearchVector(field, config="english"))
                .filter(vector=evidence_query)
                .values_list("pk", flat=True)
            )
            matching_ids = set(matches)
            for patent in page:
                if patent.pk in matching_ids:
                    excerpts.setdefault(patent.pk, {
                        "text": getattr(patent, field),
                        "source_field": field, "source_index": None,
                    })
    else:
        field = (
            "title" if effective["title_exact"] or effective["title_keywords"]
            else "abstract" if effective["abstract_keywords"] else None
        )
        if field:
            for patent in page:
                excerpts[patent.pk] = {
                    "text": getattr(patent, field),
                    "source_field": field, "source_index": None,
                }
    return excerpts


def search_patents(
    *, query=None, classification_prefix=None, title_keywords=None,
    abstract_keywords=None, title_exact=None, limit=20, offset=0,
):
    query = _text(query, "query")
    classification_prefix = _text(classification_prefix, "classification_prefix")
    if classification_prefix and not re.fullmatch(r"[A-Z0-9]+", classification_prefix):
        raise SearchInputError("classification_prefix must contain uppercase ASCII letters/digits")
    title_exact = normalized_title(_text(title_exact, "title_exact"))
    title_keywords = _keywords(title_keywords, "title_keywords")
    abstract_keywords = _keywords(abstract_keywords, "abstract_keywords")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise SearchInputError("limit must be an integer between 1 and 100")
    if type(offset) is not int or offset < 0:
        raise SearchInputError("offset must be a nonnegative integer")
    if not any((query, classification_prefix, title_exact, title_keywords, abstract_keywords)):
        raise SearchInputError("Provide effective query text or at least one filter")
    effective = {
        "query": query or None, "classification_prefix": classification_prefix or None,
        "title_keywords": title_keywords, "abstract_keywords": abstract_keywords,
        "title_exact": title_exact or None, "limit": limit, "offset": offset,
    }
    search_query = evidence_query = None
    if query:
        with connection.cursor() as cursor:
            cursor.execute("SELECT plainto_tsquery('english'::regconfig, %s)::text", [query])
            compiled_query = cursor.fetchone()[0]
        if not compiled_query:
            raise SearchInputError("query contains no searchable English lexemes")
        search_query = SearchQuery(query, config="english", search_type="plain")
        # Only database-produced, quoted lexemes enter the raw evidence query.
        evidence_query = SearchQuery(
            compiled_query.replace(" & ", " | "), config="english", search_type="raw",
        )
    candidates = Patent.objects.all()
    if search_query is not None:
        candidates = candidates.filter(search_vector=search_query)
    if classification_prefix:
        candidates = candidates.filter(classification__startswith=classification_prefix)
    if title_exact or title_keywords or abstract_keywords:
        # Deliberately sample-scale: Python casefold/alnum semantics, before paging.
        eligible = []
        for pk, title, abstract in candidates.values_list("pk", "title", "abstract").iterator():
            if title_exact and (title is None or normalized_title(title) != title_exact):
                continue
            if title_keywords and not set(title_keywords).issubset(tokens(title or "")):
                continue
            if abstract_keywords and not set(abstract_keywords).issubset(tokens(abstract or "")):
                continue
            eligible.append(pk)
        candidates = candidates.filter(pk__in=eligible)
    total = candidates.count()
    if search_query is not None:
        # Preserve stored positions/weights: pass the vector expression, not text.
        candidates = candidates.annotate(score=SearchRank(F("search_vector"), search_query))
        candidates = candidates.order_by("-score", "doc_number")
    else:
        candidates = candidates.order_by("doc_number")
    # Do not fetch retained raw JSON or the full vector for the response.
    page = list(candidates.defer("raw_record", "search_vector")[offset:offset + limit])
    excerpts = _excerpts(page, evidence_query, effective)
    return {
        "results": [{
            "doc_number": patent.doc_number, "title": patent.title,
            "abstract": patent.abstract, "classification": patent.classification,
            "bibtex": patent.bibtex, "filename": patent.filename,
            "source_file": patent.source_file, "record_index": patent.record_index,
            "score": patent.score if search_query is not None else None,
            "ranking_method": "ts_rank" if search_query is not None else "doc_number",
            "excerpt": excerpts.get(patent.pk),
        } for patent in page],
        "total_matches": total,
        "effective_request": effective,
    }
