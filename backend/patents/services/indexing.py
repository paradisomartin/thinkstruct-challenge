"""Explicit rebuild of derived search content; ingestion does not maintain it."""

import logging
from time import perf_counter

from django.db import connection, transaction


logger = logging.getLogger("thinkstruct.indexing")


def rebuild_search_index():
    """Replace every patent vector atomically using a single statement snapshot.

    Aggregate passages in source order, separately by weight. Raw JSON is never
    indexed: only the usable passages retained by ingestion contribute.
    Concurrent ingestion is not coordinated; run this after ingestion completes.
    """
    started = perf_counter()
    logger.info("Search index rebuild started")
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("""
            UPDATE patents_patent AS patent
            SET search_vector =
                setweight(to_tsvector('english'::regconfig,
                    coalesce(patent.title, '')), 'A') ||
                setweight(to_tsvector('english'::regconfig,
                    coalesce(patent.abstract, '')), 'B') ||
                setweight(to_tsvector('english'::regconfig, coalesce((
                    SELECT string_agg(text, ' ' ORDER BY source_index)
                    FROM patents_passage
                    WHERE patent_id = patent.doc_number AND source_field = 'claims'
                ), '')), 'B') ||
                setweight(to_tsvector('english'::regconfig, coalesce((
                    SELECT string_agg(text, ' ' ORDER BY source_index)
                    FROM patents_passage
                    WHERE patent_id = patent.doc_number
                        AND source_field = 'detailed_description'
                ), '')), 'D')
        """)
        updated = cursor.rowcount
    result = {"indexed": updated, "duration_seconds": round(perf_counter() - started, 6)}
    logger.info(
        "Search index rebuild completed indexed=%d duration_seconds=%.6f",
        updated, result["duration_seconds"],
    )
    return result
