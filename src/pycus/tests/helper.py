from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher

class HasItemsInOrder(BaseMatcher):
    
    def __init__(self, matchers):
        self.matchers = matchers
        
    def matches(self, sequence, mismatch_description=None): # pragma: no cover
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
                       "No item matched ").append_description_of(matcher
                    ).append_text("among candidates").append_description_of(sequence[to_match:])
                return False
        return True

    def describe_to(self, description): # pragma: no cover
        description.append_text("a sequence containing ")
        for matcher in self.matchers[:-1]:
            description.append_description_of(matcher)
            description.append_text(" followed by ")
        description.append_description_of(self.matchers[-1])
        
def has_items_in_order(*matchers):
    return HasItemsInOrder([wrap_matcher(matcher) for matcher in matchers])
