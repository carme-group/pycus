from __future__ import annotations

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher

from typing import Sequence, Any, Optional, Iterator

import contextlib
import tempfile
import shutil


class HasItemsInOrder(BaseMatcher):
    def __init__(self, matchers: Sequence[BaseMatcher]):
        self.matchers = matchers

    def matches(
        self,
        sequence: Sequence[Any],
        mismatch_description: Optional[Description] = None,
    ) -> bool:  # pragma: no cover
        things = iter(enumerate(sequence))
        to_match = 0
        for matcher in self.matchers:
            for idx, thing in things:
                if matcher.matches(thing):
                    to_match = idx
                    break
            else:
                if mismatch_description:
                    mismatch_description.append_text(
                        "No item matched "
                    ).append_description_of(matcher).append_text(
                        "among candidates"
                    ).append_description_of(
                        sequence[to_match:]
                    )
                return False
        return True

    def describe_to(self, description: Description) -> None:  # pragma: no cover
        description.append_text("a sequence containing ")
        for matcher in self.matchers[:-1]:
            description.append_description_of(matcher)
            description.append_text(" followed by ")
        description.append_description_of(self.matchers[-1])


def has_items_in_order(*matchers: Any) -> HasItemsInOrder:
    return HasItemsInOrder([wrap_matcher(matcher) for matcher in matchers])


@contextlib.contextmanager
def temp_dir() -> Iterator[str]:
    try:
        dirname = tempfile.mkdtemp()
        yield dirname
    finally:
        shutil.rmtree(dirname)
