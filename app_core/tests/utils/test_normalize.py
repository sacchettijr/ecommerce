from utils.normalize import normalize_email, normalize_whitespace

# ------------------------------------------------------------ normalize_whitespace


def test_normalize_whitespace_collapses_internal_runs_of_spaces() -> None:
    assert normalize_whitespace(name="Jane   Middle    Doe") == "Jane Middle Doe"


def test_normalize_whitespace_trims_leading_and_trailing_spaces() -> None:
    assert normalize_whitespace(name="  Jane Doe  ") == "Jane Doe"


def test_normalize_whitespace_collapses_tabs_and_newlines_too() -> None:
    assert normalize_whitespace(name="Jane\tDoe\n") == "Jane Doe"


# ----------------------------------------------------------------- normalize_email


def test_normalize_email_lowercases_the_whole_address() -> None:
    assert normalize_email("Jane.DOE@EXAMPLE.com") == "jane.doe@example.com"


def test_normalize_email_strips_surrounding_whitespace() -> None:
    assert normalize_email("  jane@example.com  ") == "jane@example.com"
