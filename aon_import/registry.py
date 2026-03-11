from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aon_import.contracts import Parser, Renderer
from aon_import.discover import TYPE_TO_ENDPOINT
from aon_import.handlers.generic import GenericParser, GenericRenderer
from aon_import.models import PageType


@dataclass(frozen=True)
class EndpointHandler:
    parser: Parser[Any]
    renderer: Renderer[Any]


class EndpointRegistry:
    def __init__(self) -> None:
        self._handlers: dict[PageType, EndpointHandler] = {}

    def register(self, page_type: PageType, handler: EndpointHandler) -> None:
        self._handlers[page_type] = handler

    def get(self, page_type: PageType) -> EndpointHandler:
        if page_type not in self._handlers:
            raise KeyError(f"No handler registered for page type '{page_type}'")
        return self._handlers[page_type]

    def supports(self, page_type: PageType) -> bool:
        return page_type in self._handlers

    def missing_types(self, page_types: set[PageType]) -> set[PageType]:
        return {page_type for page_type in page_types if page_type not in self._handlers}


def build_default_registry() -> EndpointRegistry:
    registry = EndpointRegistry()
    generic_handler = EndpointHandler(parser=GenericParser(), renderer=GenericRenderer())
    for page_type in TYPE_TO_ENDPOINT:
        registry.register(page_type, generic_handler)
    return registry
