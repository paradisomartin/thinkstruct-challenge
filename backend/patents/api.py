"""Thin HTTP adapter; retrieval and normalization remain in the search service."""

import logging

from django.db import DatabaseError
from ninja import Query, Router

from patents.schemas import SearchError, SearchRequest, SearchResponse
from patents.services.search import SearchInputError, search_patents


logger = logging.getLogger("thinkstruct.search")
router = Router(tags=["patents"])


@router.get("/search", response={200: SearchResponse, 422: SearchError, 503: SearchError})
def search(request, filters: Query[SearchRequest]):
    """Rank patents with AND text semantics and optional AND metadata filters.

    Repeat title_keywords/abstract_keywords for multiple literal tokens.
    Excerpts retain original text and source positions; a passage may explain
    only part of a cross-field query. Rebuild the index after ingestion.
    """
    try:
        return 200, search_patents(**filters.model_dump())
    except SearchInputError as exc:
        return 422, {"detail": str(exc)}
    except DatabaseError:
        logger.warning("Patent search unavailable: database operation failed")
        return 503, {"detail": "Search temporarily unavailable"}
