"""Thin HTTP adapter; retrieval and normalization remain in the search service."""

import logging

from django.db import DatabaseError
from ninja import Query, Router

from api.v1.patents.schemas import ExploreRequest, ExploreResponse, SearchError, SearchRequest, SearchResponse
from patents.services.explore import explore_patents
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


@router.get("/explore", response={200: ExploreResponse, 422: SearchError, 503: SearchError})
def explore(request, filters: Query[ExploreRequest]):
    """Browse/search with linked counts over all filtered patents, before paging.

    Classification groups use three-character prefixes with four-character children.
    Source week is the date on the source JSON batch, not a legal filing date.
    Date bounds are inclusive; empty inputs browse all patents. Counts apply all
    active filters, rather than offering disjunctive facets.
    """
    try:
        return 200, explore_patents(**filters.model_dump())
    except SearchInputError as exc:
        return 422, {"detail": str(exc)}
    except DatabaseError:
        logger.warning("Patent exploration unavailable: database operation failed")
        return 503, {"detail": "Search temporarily unavailable"}
