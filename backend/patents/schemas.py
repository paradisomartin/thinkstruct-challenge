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


class SearchError(Schema):
    # Ninja's parameter validation uses a list; domain validation uses text.
    detail: str | list[dict[str, Any]]
