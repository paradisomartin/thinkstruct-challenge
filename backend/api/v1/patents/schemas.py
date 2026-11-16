from datetime import date
from typing import Any, Literal

from ninja import Schema
from pydantic import Field


class SearchRequest(Schema):
    query: str | None = None
    classification_prefix: str | None = None
    title_keywords: list[str] = Field(default_factory=list)
    abstract_keywords: list[str] = Field(default_factory=list)
    title_exact: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class Excerpt(Schema):
    text: str
    source_field: Literal["claims", "detailed_description", "title", "abstract"]
    source_index: int | None


class PatentResult(Schema):
    doc_number: str
    title: str | None
    abstract: str | None
    classification: str | None
    bibtex: str | None
    filename: str | None
    source_file: str
    record_index: int
    score: float | None
    ranking_method: Literal["ts_rank", "doc_number"]
    excerpt: Excerpt | None


class SearchResponse(Schema):
    results: list[PatentResult]
    total_matches: int
    effective_request: SearchRequest


class ExploreRequest(SearchRequest):
    source_week_from: date | None = None
    source_week_to: date | None = None


class ExplorePatentResult(PatentResult):
    source_week: date | None


class ClassificationBucket(Schema):
    prefix: str
    count: int


class ClassificationFacet(ClassificationBucket):
    children: list[ClassificationBucket]


class SourceWeekBucket(Schema):
    source_week: date
    count: int


class ExploreResponse(Schema):
    results: list[ExplorePatentResult]
    total_matches: int
    effective_request: ExploreRequest
    classification_facets: list[ClassificationFacet]
    unclassified_count: int
    source_weeks: list[SourceWeekBucket]
    unknown_source_week_count: int


class SearchError(Schema):
    # Ninja's parameter validation uses a list; domain validation uses text.
    detail: str | list[dict[str, Any]]
