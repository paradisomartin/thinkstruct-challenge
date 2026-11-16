"""Linked-view data on one PostgreSQL snapshot; metadata aggregation is sample-scale."""

from collections import Counter, defaultdict
from datetime import date
import re

from django.db import connection, transaction

from patents.services.search import SearchInputError, prepare_search, render_search


def source_week(source_file):
    """Date on a weekly JSON batch, not a verified legal filing date."""
    match = re.fullmatch(r"patents_ipa(\d{2})(\d{2})(\d{2})\.json", source_file.rsplit("/", 1)[-1])
    if not match:
        return None
    year, month, day = map(int, match.groups())
    try:
        return date(2000 + year, month, day)
    except ValueError:
        return None


def _date_bound(value, name):
    if value is None or type(value) is date:
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise SearchInputError(f"{name} must be a valid YYYY-MM-DD date")


def explore_patents(
    *, query=None, classification_prefix=None, title_keywords=None,
    abstract_keywords=None, title_exact=None, limit=20, offset=0,
    source_week_from=None, source_week_to=None,
):
    """Own the read transaction so all views see the same data version.

    Call outside an existing transaction. The HTTP adapter uses autocommit;
    transaction-level settings revert on exit, including on failure.
    """
    start = _date_bound(source_week_from, "source_week_from")
    end = _date_bound(source_week_to, "source_week_to")
    if start and end and start > end:
        raise SearchInputError("source_week_from must not be later than source_week_to")
    if connection.in_atomic_block:
        raise RuntimeError("explore_patents must run outside an existing transaction")
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        candidates, search_query, evidence_query, effective = prepare_search(
            query=query, classification_prefix=classification_prefix,
            title_keywords=title_keywords, abstract_keywords=abstract_keywords,
            title_exact=title_exact, limit=limit, offset=offset, allow_empty=True,
        )
        effective.update(source_week_from=start, source_week_to=end)
        eligible = {}
        classifications = defaultdict(Counter)
        weeks = Counter()
        unclassified = undated = 0
        # Only compact metadata is scanned; raw JSON/text/vectors stay in PostgreSQL.
        for pk, code, source in candidates.values_list("pk", "classification", "source_file").iterator():
            week = source_week(source)
            if (start or end) and (
                week is None or (start and week < start) or (end and week > end)
            ):
                continue
            eligible[pk] = week
            if code and re.fullmatch(r"[A-Z][0-9]{2}[A-Z][A-Z0-9]*", code):
                classifications[code[:3]][code[:4]] += 1
            else:
                unclassified += 1
            if week is None:
                undated += 1
            else:
                weeks[week] += 1
        response = render_search(
            candidates.filter(pk__in=eligible), search_query, evidence_query,
            effective, total=len(eligible),
        )
        for result in response["results"]:
            result["source_week"] = eligible[result["doc_number"]]
        response.update(
            classification_facets=[
                {
                    "prefix": prefix,
                    "count": sum(children.values()),
                    "children": [
                        {"prefix": child, "count": count}
                        for child, count in sorted(children.items())
                    ],
                }
                for prefix, children in sorted(classifications.items())
            ],
            unclassified_count=unclassified,
            source_weeks=[
                {"source_week": week, "count": count}
                for week, count in sorted(weeks.items())
            ],
            unknown_source_week_count=undated,
        )
        return response
