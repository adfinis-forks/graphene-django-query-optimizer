from typing import Any, NamedTuple

import pytest
from graphql_relay import offset_to_cursor

from query_optimizer.validators import PaginationArgs, validate_pagination_args
from tests.helpers import parametrize_helper


class PaginationInput(NamedTuple):
    first: Any = None
    last: Any = None
    offset: Any = None
    after: Any = None
    before: Any = None
    max_limit: Any = None


class Params(NamedTuple):
    pagination_input: PaginationInput
    output: PaginationArgs
    errors: str | None


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "first": Params(
                pagination_input=PaginationInput(),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors=None,
            ),
            "last": Params(
                pagination_input=PaginationInput(last=1),
                output=PaginationArgs(after=None, before=None, first=None, last=1, size=0),
                errors=None,
            ),
            "offset": Params(
                pagination_input=PaginationInput(offset=1),
                output=PaginationArgs(after=1, before=None, first=None, last=None, size=0),
                errors=None,
            ),
            "after": Params(
                pagination_input=PaginationInput(after=offset_to_cursor(0)),
                # Add 1 to after to make it exclusive in slicing.
                output=PaginationArgs(after=1, before=None, first=None, last=None, size=0),
                errors=None,
            ),
            "before": Params(
                pagination_input=PaginationInput(before=offset_to_cursor(0)),
                output=PaginationArgs(after=None, before=0, first=None, last=None, size=0),
                errors=None,
            ),
            "max limit": Params(
                pagination_input=PaginationInput(max_limit=1),
                output=PaginationArgs(after=None, before=None, first=1, last=None, size=0),
                errors=None,
            ),
            "first zero": Params(
                pagination_input=PaginationInput(first=0),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'first' must be a positive integer.",
            ),
            "last zero": Params(
                pagination_input=PaginationInput(last=0),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'last' must be a positive integer.",
            ),
            "first negative": Params(
                pagination_input=PaginationInput(first=-1),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'first' must be a positive integer.",
            ),
            "last negative": Params(
                pagination_input=PaginationInput(last=-1),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'last' must be a positive integer.",
            ),
            "first exceeds max limit": Params(
                pagination_input=PaginationInput(first=2, max_limit=1),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Requesting first 2 records exceeds the limit of 1.",
            ),
            "last exceeds max limit": Params(
                pagination_input=PaginationInput(last=2, max_limit=1),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Requesting last 2 records exceeds the limit of 1.",
            ),
            "offset zero": Params(
                pagination_input=PaginationInput(offset=0),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument `offset` must be a positive integer.",
            ),
            "after negative": Params(
                pagination_input=PaginationInput(after=offset_to_cursor(-1)),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="The node pointed with `after` does not exist.",
            ),
            "before negative": Params(
                pagination_input=PaginationInput(before=offset_to_cursor(-1)),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="The node pointed with `before` does not exist.",
            ),
            "after before": Params(
                pagination_input=PaginationInput(after=offset_to_cursor(1), before=offset_to_cursor(0)),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="The node pointed with `after` must be before the node pointed with `before`.",
            ),
            "offset after": Params(
                pagination_input=PaginationInput(offset=1, after=offset_to_cursor(0)),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Can only use either `offset` or `before`/`after` for pagination.",
            ),
            "offset before": Params(
                pagination_input=PaginationInput(offset=1, before=offset_to_cursor(0)),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Can only use either `offset` or `before`/`after` for pagination.",
            ),
            "after not int": Params(
                pagination_input=PaginationInput(after="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="The node pointed with `after` does not exist.",
            ),
            "before not int": Params(
                pagination_input=PaginationInput(before="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="The node pointed with `before` does not exist.",
            ),
            "first not int": Params(
                pagination_input=PaginationInput(first="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'first' must be a positive integer.",
            ),
            "last not int": Params(
                pagination_input=PaginationInput(last="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument 'last' must be a positive integer.",
            ),
            "offset not int": Params(
                pagination_input=PaginationInput(offset="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors="Argument `offset` must be a positive integer.",
            ),
            "max limit not int": Params(
                pagination_input=PaginationInput(max_limit="0"),
                output=PaginationArgs(after=None, before=None, first=None, last=None, size=0),
                errors=None,
            ),
        }
    ),
)
def test_validate_pagination_args(pagination_input, output, errors):
    try:
        args = validate_pagination_args(**pagination_input._asdict())
    except ValueError as error:
        if errors is None:
            pytest.fail(f"Unexpected error: {error}")
        assert str(error) == errors
    else:
        assert args == output
